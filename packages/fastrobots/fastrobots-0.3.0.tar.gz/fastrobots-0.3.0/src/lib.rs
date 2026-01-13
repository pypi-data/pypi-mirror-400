use memchr::memchr;
use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;
use smallvec::{smallvec, SmallVec};

// ===========================================================================
// CONSTANTS & BITFLAGS
// ===========================================================================

const WILDCARD: u8 = b'*';
const END_ANCHOR: u8 = b'$';
const NEWLINE: u8 = b'\n';
const COLON: u8 = b':';
const HASH: u8 = b'#';

const FLAG_ALLOWED: u8 = 1;      // Bit 0: 1 = Allow, 0 = Disallow
const FLAG_WILDCARD: u8 = 2;     // Bit 1: Pattern contains '*'
const FLAG_END_ANCHOR: u8 = 4;   // Bit 2: Pattern ends with '$'

// ===========================================================================
// DATA STRUCTURES (Cache Optimized)
// ===========================================================================

/// Highly packed rule structure (8 bytes).
/// Fits 8 rules per x86_64 cache line (64 bytes) for maximum throughput.
#[repr(C)]
#[derive(Debug, Clone, Copy)]
struct PackedRule {
    offset: u32,  // Offset into the byte arena
    len: u16,     // Length of the path pattern
    meta: u8,     // Bitflags
    _padding: u8, // Padding for alignment
}

/// Metadata for a User-Agent block.
#[derive(Debug, Clone, Default)]
struct AgentData {
    rule_start: u32,
    rule_count: u32,
    crawl_delay: Option<f64>,
}

#[pyclass(frozen)]
pub struct Robots {
    /// Contiguous storage for all rule path bytes (The Arena).
    arena: Box<[u8]>,
    /// Flattened array of all rules for all agents, sorted by specificity.
    rules: Box<[PackedRule]>,
    /// Agents map: (Name Bytes, Data).
    /// A linear scan over this array is faster than a HashMap for the small N
    /// typical in robots.txt (< 50 items) due to predictive CPU fetching.
    agents: Box<[(Box<[u8]>, AgentData)]>,
    /// Optimized fallback for "*"
    wildcard_agent: AgentData,
    /// Sitemap URLs
    sitemaps: Vec<String>,
}

// ===========================================================================
// CUSTOM WILDCARD MATCHER (Regex Killer)
// ===========================================================================

/// Specialized recursive matcher for robots.txt wildcards.
/// Uses SIMD (memchr) to skip bytes rapidly, avoiding state machine overhead.
#[inline(always)]
fn matches_pattern(pattern: &[u8], text: &[u8], must_end: bool) -> bool {
    let mut p_idx = 0;
    let mut t_idx = 0;
    let p_len = pattern.len();
    let t_len = text.len();

    while p_idx < p_len && t_idx < t_len {
        let p_char = unsafe { *pattern.get_unchecked(p_idx) };

        // Handle Wildcard '*'
        if p_char == WILDCARD {
            // Skip consecutive wildcards
            while p_idx + 1 < p_len && unsafe { *pattern.get_unchecked(p_idx + 1) } == WILDCARD {
                p_idx += 1;
            }

            // Trailing * matches everything
            if p_idx == p_len - 1 {
                return true;
            }

            p_idx += 1;
            let next_char = unsafe { *pattern.get_unchecked(p_idx) };

            // SIMD scan for the character following the wildcard
            let mut offset = 0;
            let search_slice = &text[t_idx..];

            // Backtracking loop using memchr for speed
            while let Some(pos) = memchr(next_char, &search_slice[offset..]) {
                // Try to match from this position
                let abs_pos = t_idx + offset + pos;
                // Recursive call (depth bounded by pattern length)
                if matches_pattern(&pattern[p_idx..], &text[abs_pos..], must_end) {
                    return true;
                }
                // If failed, continue searching in remainder
                offset += pos + 1;
            }
            return false;
        }

        // Exact char match
        if p_char != unsafe { *text.get_unchecked(t_idx) } {
            return false;
        }

        p_idx += 1;
        t_idx += 1;
    }

    // Pattern exhausted
    if p_idx == p_len {
        // If the rule had an End Anchor ($), we must ensure we consumed the whole text
        if must_end {
            return t_idx == t_len;
        }
        return true; // Prefix match successful
    }

    // Text exhausted, check if remaining pattern is just '*'
    if p_idx == p_len - 1 && unsafe { *pattern.get_unchecked(p_idx) } == WILDCARD {
        return true;
    }

    false
}

// ===========================================================================
// IMPLEMENTATION
// ===========================================================================

impl Robots {
    /// Internal helper: Finds the most specific agent rules for a user-agent.
    /// Expects `ua_lower` to be a lowercased byte slice.
    #[inline(always)]
    fn find_agent_for_normalized_ua(&self, ua_lower: &[u8]) -> &AgentData {
        let mut best_len = 0;
        let mut target_data = &self.wildcard_agent;

        // Optimized linear scan.
        // RFC 9309: "The most specific match is the one with the longest user-agent identifier."
        for (name, data) in self.agents.iter() {
            let n_len = name.len();
            if n_len > best_len && n_len <= ua_lower.len() {
                // Substring check: Does the User-Agent contain this token?
                // Using windows iterator is extremely fast for short agent names.
                if ua_lower.windows(n_len).any(|w| w == &**name) {
                    best_len = n_len;
                    target_data = data;
                }
            }
        }
        target_data
    }

    /// Internal helper: Checks a path against a specific set of rules.
    #[inline(always)]
    fn check_rules_for_agent(&self, path: &[u8], agent: &AgentData) -> bool {
        if agent.rule_count == 0 {
            return true;
        }

        let start = agent.rule_start as usize;
        let end = start + agent.rule_count as usize;

        // Safety: Indices are guaranteed valid by the parser logic
        let rules_slice = unsafe { self.rules.get_unchecked(start..end) };

        for rule in rules_slice {
            let r_start = rule.offset as usize;
            let r_end = r_start + rule.len as usize;

            // Safety: Offsets are guaranteed valid by arena construction
            let pattern = unsafe { self.arena.get_unchecked(r_start..r_end) };

            let is_match = if (rule.meta & FLAG_WILDCARD) == 0 {
                // FAST PATH: No wildcards
                if (rule.meta & FLAG_END_ANCHOR) == 0 {
                    // Simple prefix match
                    path.starts_with(pattern)
                } else {
                    // Exact match (End anchor implies equality)
                    path == pattern
                }
            } else {
                // SLOW PATH: Wildcard matching
                matches_pattern(pattern, path, (rule.meta & FLAG_END_ANCHOR) != 0)
            };

            if is_match {
                return (rule.meta & FLAG_ALLOWED) != 0;
            }
        }

        true // Default allowed
    }
}

#[pymethods]
impl Robots {
    #[staticmethod]
    fn parse(content: &str) -> PyResult<Self> {
        let input = content.as_bytes();
        // Heuristic: Arena usually takes ~50% of file size
        let mut arena = Vec::with_capacity(input.len() / 2);
        struct BuildAgent {
            name: Vec<u8>,
            rules: Vec<PackedRule>,
            crawl_delay: Option<f64>,
        }

        let mut temp_agents: Vec<BuildAgent> = Vec::with_capacity(8);
        // Stack-allocated vector for tracking current agents group
        let mut current_indices: SmallVec<[usize; 4]> = smallvec![];
        let mut sitemaps = Vec::new();

        let mut ptr = 0;
        let len = input.len();

        while ptr < len {
            // 1. Find end of line using SIMD
            let end = memchr(NEWLINE, &input[ptr..]).map_or(len, |i| ptr + i);
            let mut line = &input[ptr..end];
            ptr = end + 1;

            // 2. Strip comments (fast scan)
            if let Some(pos) = memchr(HASH, line) {
                line = &line[..pos];
            }
            // 3. Trim whitespace (byte level)
            while !line.is_empty() && line[0].is_ascii_whitespace() { line = &line[1..]; }
            while !line.is_empty() && line[line.len()-1].is_ascii_whitespace() { line = &line[..line.len()-1]; }

            if line.is_empty() { continue; }

            // 4. Split Key: Value
            let colon = match memchr(COLON, line) {
                Some(i) => i,
                None => continue,
            };

            let key = &line[..colon];
            let val_full = &line[colon+1..];
            // Trim value start
            let mut v_start = 0;
            while v_start < val_full.len() && val_full[v_start].is_ascii_whitespace() { v_start += 1; }
            let val = &val_full[v_start..];

            // 5. Parse Directive
            // "user-agent" len=10
            if key.len() == 10 && key.eq_ignore_ascii_case(b"user-agent") {
                let mut name = val.to_vec();
                name.make_ascii_lowercase();

                // Grouping Logic: If previous group had rules/delay, start new group.
                if !current_indices.is_empty() {
                    let first = current_indices[0];
                    if !temp_agents[first].rules.is_empty() || temp_agents[first].crawl_delay.is_some() {
                        current_indices.clear();
                    }
                }

                if let Some(pos) = temp_agents.iter().position(|a: &BuildAgent| a.name == name) {
                    current_indices.push(pos);
                } else {
                    current_indices.push(temp_agents.len());
                    temp_agents.push(BuildAgent { name, rules: Vec::new(), crawl_delay: None });
                }

            } else if key.len() == 8 && key.eq_ignore_ascii_case(b"disallow") {
                if val.is_empty() { continue; }
                let has_wc = memchr(WILDCARD, val).is_some();
                let has_end = val.last() == Some(&END_ANCHOR);

                // If ends with $, don't store the $ in the arena, just set the flag
                let store_len = if has_end { val.len() - 1 } else { val.len() };

                let meta = if has_wc { FLAG_WILDCARD } else { 0 } |
                           if has_end { FLAG_END_ANCHOR } else { 0 };

                let offset = arena.len() as u32;
                arena.extend_from_slice(&val[..store_len]);

                let rule = PackedRule { offset, len: store_len as u16, meta, _padding: 0 };
                for &idx in &current_indices { temp_agents[idx].rules.push(rule); }

            } else if key.len() == 5 && key.eq_ignore_ascii_case(b"allow") {
                if val.is_empty() { continue; }
                let has_wc = memchr(WILDCARD, val).is_some();
                let has_end = val.last() == Some(&END_ANCHOR);
                let store_len = if has_end { val.len() - 1 } else { val.len() };

                let meta = FLAG_ALLOWED |
                           if has_wc { FLAG_WILDCARD } else { 0 } |
                           if has_end { FLAG_END_ANCHOR } else { 0 };

                let offset = arena.len() as u32;
                arena.extend_from_slice(&val[..store_len]);

                let rule = PackedRule { offset, len: store_len as u16, meta, _padding: 0 };
                for &idx in &current_indices { temp_agents[idx].rules.push(rule); }

            } else if key.len() == 11 && key.eq_ignore_ascii_case(b"crawl-delay") {
                // Trust f64 parse to fail on garbage
                if let Ok(s) = std::str::from_utf8(val) {
                    if let Ok(d) = s.parse::<f64>() {
                        for &idx in &current_indices { temp_agents[idx].crawl_delay = Some(d); }
                    }
                }
            } else if key.len() == 7 && key.eq_ignore_ascii_case(b"sitemap") {
                 if let Ok(s) = std::str::from_utf8(val) { sitemaps.push(s.to_string()); }
            }
        }

        // 6. Finalize & Flatten
        let mut final_rules = Vec::new();
        let mut final_agents = Vec::with_capacity(temp_agents.len());
        let mut wildcard_agent = AgentData::default();

        for mut agent in temp_agents {
            // Sort: Length Descending. If equal, Allow > Disallow.
            agent.rules.sort_unstable_by(|a, b| {
                b.len.cmp(&a.len).then_with(|| (a.meta & FLAG_ALLOWED).cmp(&(b.meta & FLAG_ALLOWED)))
            });

            let data = AgentData {
                rule_start: final_rules.len() as u32,
                rule_count: agent.rules.len() as u32,
                crawl_delay: agent.crawl_delay,
            };
            final_rules.extend(agent.rules);

            if agent.name == b"*" {
                wildcard_agent = data;
            } else {
                final_agents.push((agent.name.into_boxed_slice(), data));
            }
        }

        Ok(Robots {
            arena: arena.into_boxed_slice(),
            rules: final_rules.into_boxed_slice(),
            agents: final_agents.into_boxed_slice(),
            wildcard_agent,
            sitemaps,
        })
    }

    #[staticmethod]
    fn parse_optimized(content: &str) -> PyResult<Self> {
        Self::parse(content)
    }

    fn allowed(&self, path: &str, user_agent: &str) -> bool {
        // Stack-allocated buffer for zero-heap lowercasing
        let mut ua_buf = [0u8; 512];
        let ua_bytes = user_agent.as_bytes();
        let n = ua_bytes.len().min(512);

        // Fast lowercasing loop
        for i in 0..n {
            let b = unsafe { *ua_bytes.get_unchecked(i) };
            unsafe { *ua_buf.get_unchecked_mut(i) = b.to_ascii_lowercase(); }
        }
        let ua_lower = &ua_buf[..n];

        let agent = self.find_agent_for_normalized_ua(ua_lower);
        self.check_rules_for_agent(path.as_bytes(), agent)
    }

    /// Batch processing for high-throughput
    fn allowed_batch(&self, paths: Vec<String>, user_agent: &str) -> Vec<bool> {
        // Normalize UA once
        let mut ua_buf = [0u8; 512];
        let ua_bytes = user_agent.as_bytes();
        let n = ua_bytes.len().min(512);
        for i in 0..n {
            unsafe { *ua_buf.get_unchecked_mut(i) = (*ua_bytes.get_unchecked(i)).to_ascii_lowercase(); }
        }
        let agent = self.find_agent_for_normalized_ua(&ua_buf[..n]);

        // Check all paths against the same agent data
        paths.iter()
             .map(|p| self.check_rules_for_agent(p.as_bytes(), agent))
             .collect()
    }

    fn crawl_delay(&self, user_agent: &str) -> Option<f64> {
        let mut ua_buf = [0u8; 512];
        let ua_bytes = user_agent.as_bytes();
        let n = ua_bytes.len().min(512);
        for i in 0..n {
             unsafe { *ua_buf.get_unchecked_mut(i) = (*ua_bytes.get_unchecked(i)).to_ascii_lowercase(); }
        }

        let agent = self.find_agent_for_normalized_ua(&ua_buf[..n]);
        agent.crawl_delay
    }

    #[getter]
    fn sitemaps(&self) -> Vec<String> {
        self.sitemaps.clone()
    }

    #[getter]
    fn user_agents(&self) -> Vec<String> {
        let mut result: Vec<String> = self.agents.iter()
            .map(|(n, _)| String::from_utf8_lossy(n).into_owned())
            .collect();
        // Include wildcard if it has rules
        if self.wildcard_agent.rule_count > 0 || self.wildcard_agent.crawl_delay.is_some() {
            result.push("*".to_string());
        }
        result
    }

    fn agent(slf: Py<Self>, name: String) -> Agent {
        Agent { owner: slf, name }
    }

    fn __repr__(&self) -> String {
        format!("Robots(agents={}, sitemaps={})", self.agents.len(), self.sitemaps.len())
    }
}

/// Agent wrapper to maintain Python API compatibility.
/// Holds a reference to the immutable Robots structure.
#[pyclass]
pub struct Agent {
    owner: Py<Robots>,
    name: String,
}

#[pymethods]
impl Agent {
    fn allowed(&self, py: Python, path: &str) -> bool {
        self.owner.borrow(py).allowed(path, &self.name)
    }

    #[getter]
    fn delay(&self, py: Python) -> Option<f64> {
        self.owner.borrow(py).crawl_delay(&self.name)
    }

    #[getter]
    fn name(&self) -> &str {
        &self.name
    }

    fn __repr__(&self) -> String {
        format!("Agent(name='{}')", self.name)
    }
}

// -----------------------------------------------------------------------------
// HELPER FUNCTIONS
// -----------------------------------------------------------------------------

#[pyfunction]
fn robots_url(url: &str) -> PyResult<String> {
    let parsed = url::Url::parse(url).map_err(|e| PyValueError::new_err(e.to_string()))?;
    let host = parsed.host_str().ok_or_else(|| PyValueError::new_err("URL has no host"))?;
    match parsed.port() {
        Some(p) => Ok(format!("{}://{}:{}/robots.txt", parsed.scheme(), host, p)),
        None => Ok(format!("{}://{}/robots.txt", parsed.scheme(), host)),
    }
}

#[pyfunction]
fn url_path(url: &str) -> PyResult<String> {
    let parsed = url::Url::parse(url).map_err(|e| PyValueError::new_err(e.to_string()))?;
    Ok(parsed.path().to_string())
}

#[pymodule]
fn _core(_py: Python, m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<Robots>()?;
    m.add_class::<Agent>()?;
    m.add_function(wrap_pyfunction!(robots_url, m)?)?;
    m.add_function(wrap_pyfunction!(url_path, m)?)?;
    Ok(())
}
