# File: backend/mytools/parse_best_practices.py

from typing import List, Dict, Any, Optional, Tuple
from pydantic import BaseModel
import re
from dataclasses import dataclass, field


@dataclass
class NodeInfo:
    """Extracted node information from best practices"""
    name: str
    node_id: str  # e.g., "n8n-nodes-base.httpRequest"
    purpose: str
    category: str  # trigger, action, control, transform, ai
    pitfalls: List[str] = field(default_factory=list)
    is_recommended: bool = True
    alternatives: List[str] = field(default_factory=list)
    use_cases: List[str] = field(default_factory=list)
    input_connections: List[str] = field(default_factory=list)  # Added: Input node names
    output_connections: List[str] = field(default_factory=list)  # Added: Output node names


@dataclass
class WorkflowPattern:
    """Workflow pattern extracted from best practices"""
    name: str
    description: str
    nodes_sequence: List[str]  # Node names in order
    connections_description: str


class BestPracticeParser:
    """
    Parses best practices documentation string to extract:
    - Recommended nodes with IDs
    - Node purposes and pitfalls
    - Workflow patterns
    - Critical instructions
    """
    
    def __init__(self, best_practices_text: str):
        self.text = best_practices_text
        self.nodes: List[NodeInfo] = []
        self.patterns: List[WorkflowPattern] = []
        self.critical_instructions: List[str] = []
        self.general_guidelines: List[str] = []
        self.input_connections: List[str]= []
        self.output_connections: List[str]= []
        
        self._parse()
    
    def _parse(self):
        """Main parsing logic"""
        self._extract_critical_instructions()
        self._extract_recommended_nodes()
        self._extract_workflow_patterns()
        self._extract_general_guidelines()
        self._assign_connections()
    
    def _extract_critical_instructions(self):
        """Extract CRITICAL marked instructions"""
        critical_pattern = r'CRITICAL:(.*?)(?=\n\n|\n[A-Z]|$)'
        matches = re.findall(critical_pattern, self.text, re.DOTALL | re.IGNORECASE)
        
        for match in matches:
            instruction = match.strip()
            if instruction:
                self.critical_instructions.append(instruction)
    
    def _extract_recommended_nodes(self):
        """Extract node information from Recommended Nodes section"""
        
        # Pattern 1: Nodes with full IDs like @n8n/n8n-nodes-langchain.chatTrigger
        # Pattern: ### Node Name (@package.nodeId) or (package.nodeId)
        # Also match **Node Name** (package.nodeId): for inline bold nodes
        node_patterns = [
            r'###\s+(.+?)\s+\((@?[\w/-]+\.[\w]+)\)',  # Header format
            r'\*\*(.+?)\*\*\s+\((@?[\w/-]+\.[\w]+)\):',  # Bold inline format
        ]
        
        for pattern in node_patterns:
            node_matches = re.finditer(pattern, self.text)
            
            for match in node_matches:
                node_name = match.group(1).strip()
                node_id = match.group(2).strip()
                
                # Skip if already added
                # if any(n.node_id == node_id for n in self.nodes):
                #     continue
                
                # Get the section text after this node (until next ### or end)
                start_pos = match.end()
                next_section = re.search(r'\n(?:###|\*\*[A-Z])', self.text[start_pos:])
                end_pos = start_pos + next_section.start() if next_section else len(self.text)
                section_text = self.text[start_pos:end_pos]
                
                # Extract purpose
                purpose = self._extract_purpose(section_text)
                
                # Extract pitfalls
                pitfalls = self._extract_pitfalls(section_text)
                
                # Determine category
                category = self._determine_category(node_name, node_id, section_text)
                
                # Extract use cases
                use_cases = self._extract_use_cases(section_text)
                
                # Extract alternatives
                alternatives = self._extract_alternatives(section_text, node_name)
                
                node_info = NodeInfo(
                    name=node_name,
                    node_id=node_id,
                    purpose=purpose,
                    category=category,
                    pitfalls=pitfalls,
                    use_cases=use_cases,
                    alternatives=alternatives
                )
                
                self.nodes.append(node_info)
        
        # Also extract nodes mentioned in lists (without full headers)
        self._extract_list_nodes()
    
    def _extract_list_nodes(self):
        """Extract nodes from bulleted lists with IDs"""
        # Pattern: - Node Name (package.nodeId)
        list_pattern = r'-\s+(.+?)\s+\((@?[\w/-]+\.[\w]+)\)'
        
        list_matches = re.finditer(list_pattern, self.text)
        
        for match in list_matches:
            node_name = match.group(1).strip()
            node_id = match.group(2).strip()
            
            # Skip if already added
            # if any(n.node_id == node_id for n in self.nodes):
            #     continue
            
            # Get surrounding context
            start = max(0, match.start() - 200)
            end = min(len(self.text), match.end() + 200)
            context = self.text[start:end]
            
            purpose = self._extract_purpose_from_context(context, node_name)
            category = self._determine_category(node_name, node_id, context)
            
            node_info = NodeInfo(
                name=node_name,
                node_id=node_id,
                purpose=purpose,
                category=category
            )
            
            self.nodes.append(node_info)
    
    def _extract_purpose(self, section_text: str) -> str:
        """Extract purpose from node section"""
        # Pattern 1: Explicit "Purpose:" label
        purpose_match = re.search(r'Purpose:\s*(.+?)(?=\n\n|\nPitfalls:|\nUse cases?:|\n[A-Z][a-z]+:|###|\*\*[A-Z]|$)', 
                                  section_text, re.DOTALL | re.IGNORECASE)
        if purpose_match:
            purpose = purpose_match.group(1).strip()
            # Clean up multi-line purposes
            purpose = ' '.join(line.strip() for line in purpose.split('\n') if line.strip())
            return purpose
        
        # Pattern 2: Text right after "- Purpose:" in bullet points
        bullet_purpose = re.search(r'-\s+Purpose:\s*(.+?)(?=\n|$)', section_text, re.IGNORECASE)
        if bullet_purpose:
            return bullet_purpose.group(1).strip()
        
        # Pattern 3: First paragraph after node header
        lines = section_text.strip().split('\n')
        for line in lines:
            line = line.strip()
            # Skip empty lines, headers, and labels
            if line and not line.startswith('#') and not line.startswith('Purpose:') and not line.startswith('Pitfalls:'):
                # If it's not a bullet point or label, use it
                if not re.match(r'^[\-\*]|^[A-Z][a-z]+:', line):
                    return line
        
        return "No purpose specified"
    
    def _extract_purpose_from_context(self, context: str, node_name: str) -> str:
        """Extract purpose from surrounding context"""
        # Look for purpose in the same line or next line
        lines = context.split('\n')
        for i, line in enumerate(lines):
            if node_name in line:
                # Check next line
                if i + 1 < len(lines):
                    next_line = lines[i + 1].strip()
                    if next_line and not next_line.startswith('-'):
                        return next_line
        return "Recommended node"
    
    def _extract_pitfalls(self, section_text: str) -> List[str]:
        """Extract pitfalls from node section"""
        pitfalls = []
        
        # Look for Pitfalls section - now handles multi-line bullets
        pitfalls_match = re.search(r'Pitfalls?:\s*\n((?:(?:\s*-\s*.+\n?)+|(?:(?!\n\n|###).)+)+)', 
                                   section_text, re.IGNORECASE | re.DOTALL)
        if pitfalls_match:
            pitfall_text = pitfalls_match.group(1).strip()
            
            # Split by bullet points, but keep multi-line content
            current_pitfall = []
            for line in pitfall_text.split('\n'):
                line = line.strip()
                if line.startswith('-'):
                    # Save previous pitfall if exists
                    if current_pitfall:
                        pitfalls.append(' '.join(current_pitfall))
                    # Start new pitfall
                    current_pitfall = [line[1:].strip()]
                elif line and current_pitfall:
                    # Continuation of previous pitfall
                    current_pitfall.append(line)
                elif not line and current_pitfall:
                    # Empty line might end the pitfall
                    break
            
            # Add the last pitfall
            if current_pitfall:
                pitfalls.append(' '.join(current_pitfall))
        
        return pitfalls
    
    def _extract_use_cases(self, section_text: str) -> List[str]:
        """Extract use cases or examples"""
        use_cases = []
        
        # Look for "For example" or "Example:"
        example_pattern = r'(?:For example|Example):\s*(.+?)(?=\n\n|$)'
        matches = re.findall(example_pattern, section_text, re.DOTALL | re.IGNORECASE)
        
        for match in matches:
            use_cases.append(match.strip())
        
        return use_cases
    
    def _extract_alternatives(self, section_text: str, node_name: str) -> List[str]:
        """Extract alternative nodes mentioned"""
        alternatives = []
        
        # Look for "rather than", "instead of", "over"
        alt_patterns = [
            r'rather than\s+([^,.]+)',
            r'instead of\s+([^,.]+)',
            r'over\s+([^,.]+?)(?:\s+(?:for|node))',
            r'alternative(?:s)?:\s*([^.]+)'
        ]
        
        for pattern in alt_patterns:
            matches = re.findall(pattern, section_text, re.IGNORECASE)
            for match in matches:
                # Clean up the match
                alt = match.strip()
                # Remove common suffixes
                alt = re.sub(r'\s+node[s]?$', '', alt, flags=re.IGNORECASE)
                if alt and alt != node_name:
                    alternatives.append(alt)
        
        return list(set(alternatives))
    
    def _determine_category(self, node_name: str, node_id: str, context: str) -> str:
        """Determine node category based on name, ID, and context"""
        name_lower = node_name.lower()
        id_lower = node_id.lower()
        context_lower = context.lower()
        
        # Trigger nodes
        if 'trigger' in name_lower or 'trigger' in id_lower:
            return 'trigger'
        if 'webhook' in name_lower or 'schedule' in name_lower:
            return 'trigger'
        
        # AI/LLM nodes
        if any(term in name_lower for term in ['ai', 'agent', 'chat model', 'llm', 'openai', 'gemini', 'grok', 'deepseek']):
            return 'ai'
        if 'langchain' in id_lower:
            return 'ai'
        
        # Control flow nodes
        if any(term in name_lower for term in ['if', 'switch', 'merge', 'split', 'loop']):
            return 'control'
        
        # Transform nodes
        if any(term in name_lower for term in ['set', 'code', 'function', 'edit', 'transform']):
            return 'transform'
        
        # Memory nodes
        if 'memory' in name_lower:
            return 'ai'
        
        # Default to action
        return 'action'
    
    def _extract_workflow_patterns(self):
        """Extract example workflow patterns"""
        
        # Look for example patterns with arrows
        pattern_regex = r'(?:Example pattern|Pattern):\s*\n((?:.*?→.*?\n?)+)'
        matches = re.finditer(pattern_regex, self.text, re.IGNORECASE)
        
        for match in matches:
            pattern_text = match.group(1).strip()
            lines = pattern_text.split('\n')
            
            for line in lines:
                if '→' in line or '->' in line:
                    # Parse the sequence
                    sequence = self._parse_pattern_line(line)
                    if sequence:
                        pattern = WorkflowPattern(
                            name="Example Pattern",
                            description=line.strip(),
                            nodes_sequence=sequence,
                            connections_description=line.strip()
                        )
                        self.patterns.append(pattern)
    def _parse_pattern_line(self, line: str) -> List[str]:
        """Parse a pattern line like 'A → B → C' into node names"""
        # Replace arrow variations
        line = line.replace('→', '->').replace('â†', '->')
        
        # Split by arrow
        parts = line.split('->')
        
        # Clean up node names
        nodes = []
        for part in parts:
            part = part.strip()
            # Remove brackets and other markers
            part = re.sub(r'[\[\]\(\)]', '', part)
            # Take first meaningful word/phrase
            node_match = re.search(r'([A-Za-z][\w\s]+?)(?:\s*(?:via|node|through)|$)', part)
            if node_match:
                nodes.append(node_match.group(1).strip())
        
        return nodes
    
    def _extract_general_guidelines(self):
        """Extract general guidelines from sections"""
        
        # Extract from sections like "Workflow Design", "Context Management", etc.
        section_pattern = r'##\s+(.+?)\n\n((?:(?!##).)+)'
        matches = re.finditer(section_pattern, self.text, re.DOTALL)
        
        for match in matches:
            section_name = match.group(1).strip()
            section_content = match.group(2).strip()
            
            # Skip "Recommended Nodes" section as we handle that separately
            if 'recommended nodes' in section_name.lower():
                continue
            
            # Extract key points (paragraphs)
            paragraphs = section_content.split('\n\n')
            for para in paragraphs:
                para = para.strip()
                if para and not para.startswith('#') and len(para) > 50:
                    self.general_guidelines.append(f"[{section_name}] {para}")
    
    def get_nodes_by_category(self, category: str) -> List[NodeInfo]:
        """Get all nodes of a specific category"""
        return [node for node in self.nodes if node.category == category]
    
    def get_required_nodes(self) -> List[NodeInfo]:
        """Get nodes that are marked as required"""
        # Look for nodes mentioned with "must", "required", "always"
        required = []
        for node in self.nodes:
            node_context = self._get_node_context(node.name)
            if any(word in node_context.lower() for word in ['must', 'required', 'always use', 'essential']):
                required.append(node)
        return required
    
    def _assign_connections(self):
        """Connect nodes sequentially based on the order they were added to self.nodes"""
        if len(self.nodes) < 2:
            return

        # self.nodes is already in the correct order from extraction
        for i in range(len(self.nodes)):
            current = self.nodes[i]
            
            # Add input from previous node
            if i > 0:
                prev = self.nodes[i - 1]
                if prev.name not in current.input_connections:
                    current.input_connections.append(prev.name)
            
            # Add output to next node
            if i < len(self.nodes) - 1:
                next_node = self.nodes[i + 1]
                if next_node.name not in current.output_connections:
                    current.output_connections.append(next_node.name)
    
    def _get_node_context(self, node_name: str) -> str:
        """Get surrounding context for a node"""
        node_pos = self.text.find(node_name)
        if node_pos == -1:
            return ""
        
        start = max(0, node_pos - 500)
        end = min(len(self.text), node_pos + 500)
        return self.text[start:end]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert parsed data to dictionary"""
        return {
            "nodes": [
                {
                    "name": node.name,
                    "node_id": node.node_id,
                    "purpose": node.purpose,
                    "category": node.category,
                    "pitfalls": node.pitfalls,
                    "use_cases": node.use_cases,
                    "alternatives": node.alternatives,
                    "is_recommended": node.is_recommended,
                    "input_connections": node.input_connections, 
                    "output_connections": node.output_connections  
                }
                for node in self.nodes
            ],
            "patterns": [
                {
                    "name": pattern.name,
                    "description": pattern.description,
                    "nodes_sequence": pattern.nodes_sequence
                }
                for pattern in self.patterns
            ],
            "critical_instructions": self.critical_instructions,
            "general_guidelines": self.general_guidelines
        }
    
    def format_summary(self) -> str:
        """Create a human-readable summary"""
        lines = ["=== Best Practices Summary ===\n"]
        
        # Nodes by category
        categories = set(node.category for node in self.nodes)
        for category in sorted(categories):
            cat_nodes = self.get_nodes_by_category(category)
            lines.append(f"\n{category.upper()} NODES ({len(cat_nodes)}):")
            for node in cat_nodes:
                lines.append(f"  • {node.name}")
                lines.append(f"    ID: {node.node_id}")
                lines.append(f"    Purpose: {node.purpose}")
                if node.pitfalls:
                    lines.append(f"    ⚠ Pitfalls: {len(node.pitfalls)}")
        
        # Patterns
        if self.patterns:
            lines.append(f"\n\nWORKFLOW PATTERNS ({len(self.patterns)}):")
            for pattern in self.patterns:
                lines.append(f"  • {' → '.join(pattern.nodes_sequence)}")
        
        # Critical instructions
        if self.critical_instructions:
            lines.append(f"\n\nCRITICAL INSTRUCTIONS ({len(self.critical_instructions)}):")
            for instruction in self.critical_instructions:
                lines.append(f"  ⚠ {instruction[:100]}...")
        
        return "\n".join(lines)


# Helper function for easy use
def parse_best_practices(text: str) -> BestPracticeParser:
    """Parse best practices text and return parser instance"""
    return BestPracticeParser(text)