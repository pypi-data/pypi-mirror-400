"""
XBRL Parser using Arelle for parsing SEC filings.
Handles both standard XBRL and iXBRL (inline XBRL) formats.
"""

import os
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
from datetime import date, datetime

from arelle import Cntlr, ModelManager
from arelle.ModelXbrl import ModelXbrl

from ..config import get_settings
from .gaap_mappings import (
    BALANCE_SHEET_MAPPINGS,
    INCOME_STATEMENT_MAPPINGS,
    CASH_FLOW_MAPPINGS,
    STATEMENT_LABELS,
)

logger = logging.getLogger(__name__)
settings = get_settings()


class XBRLParser:
    """Parses XBRL files using Arelle."""

    def __init__(self):
        # Initialize Arelle controller (silent mode)
        self.controller = Cntlr.Cntlr(logFileName="logToPrint")
        self.controller.startLogging(logFileName="logToPrint")
        self.model_manager = ModelManager.initialize(self.controller)

    def _find_xbrl_file(self, xbrl_dir: Path) -> Optional[Path]:
        """Find the main XBRL file in a directory."""
        # Priority order for file discovery
        patterns = [
            "*_htm.xml",  # iXBRL extracted
            "*-*.htm",    # iXBRL inline
            "*10k*.htm",
            "*10q*.htm",
            "*8k*.htm",
            "*.xml",
        ]

        for pattern in patterns:
            matches = list(xbrl_dir.glob(pattern))
            for match in matches:
                # Skip schema and linkbase files
                name = match.name.lower()
                if any(x in name for x in ["_lab", "_def", "_cal", "_pre", ".xsd"]):
                    continue
                return match

        # Fallback: look for any XML or HTM file
        for ext in [".xml", ".htm", ".html"]:
            for f in xbrl_dir.iterdir():
                if f.suffix.lower() == ext and "_lab" not in f.name.lower():
                    return f

        return None

    def _get_xbrl_path(self, cik: int, accession_number: str, filing_date: Optional[date] = None) -> Optional[Path]:
        """Get the path to XBRL files for a filing."""
        accession_clean = accession_number.replace("-", "")

        # Try feed/documents path first (format: /mnt/moto/feed/documents/{YYYYMMDD}/{accession}/)
        if filing_date:
            date_str = filing_date.strftime("%Y%m%d")
            feed_dir = Path(settings.feed_documents_path) / date_str / accession_number
            if feed_dir.exists():
                return feed_dir

        # Try to find in feed/documents by scanning recent dates
        feed_base = Path(settings.feed_documents_path)
        if feed_base.exists():
            # Check recent date folders
            date_folders = sorted([d for d in feed_base.iterdir() if d.is_dir()], reverse=True)
            for date_folder in date_folders[:60]:  # Check last 60 days
                xbrl_dir = date_folder / accession_number
                if xbrl_dir.exists():
                    return xbrl_dir

        # Fallback: rss_processed_filings path
        padded_cik = str(cik).zfill(10)
        current_year = datetime.now().year
        for year in range(current_year, current_year - 5, -1):
            xbrl_dir = Path(settings.xbrl_base_path) / str(year) / padded_cik / accession_clean
            if xbrl_dir.exists():
                return xbrl_dir

        return None

    def parse_filing(self, cik: int, accession_number: str, filing_date: Optional[date] = None) -> Dict[str, Any]:
        """
        Parse XBRL data from a filing.

        Returns a dict with:
        - balance_sheet: Dict of balance sheet items
        - income_statement: Dict of income statement items
        - cash_flow: Dict of cash flow items
        - metadata: Filing metadata (fiscal year, period, etc.)
        """
        xbrl_dir = self._get_xbrl_path(cik, accession_number, filing_date)
        if not xbrl_dir:
            raise FileNotFoundError(f"XBRL files not found for CIK {cik}, accession {accession_number}")

        xbrl_file = self._find_xbrl_file(xbrl_dir)
        if not xbrl_file:
            raise FileNotFoundError(f"No XBRL file found in {xbrl_dir}")

        logger.info(f"Parsing XBRL file: {xbrl_file}")

        try:
            # Load the XBRL document
            model_xbrl = self.model_manager.load(str(xbrl_file))

            if model_xbrl is None:
                raise ValueError("Failed to load XBRL document")

            # Extract facts
            facts = self._extract_facts(model_xbrl)

            # Get metadata
            metadata = self._extract_metadata(model_xbrl, facts)

            # Map facts to financial statements
            balance_sheet = self._map_to_statement(facts, BALANCE_SHEET_MAPPINGS, metadata)
            income_statement = self._map_to_statement(facts, INCOME_STATEMENT_MAPPINGS, metadata)
            cash_flow = self._map_to_statement(facts, CASH_FLOW_MAPPINGS, metadata)

            # Close the model
            self.model_manager.close()

            return {
                "balance_sheet": balance_sheet,
                "income_statement": income_statement,
                "cash_flow": cash_flow,
                "metadata": metadata,
            }

        except Exception as e:
            logger.error(f"Error parsing XBRL: {e}")
            self.model_manager.close()
            raise

    def _extract_facts(self, model_xbrl: ModelXbrl) -> Dict[str, List[Dict[str, Any]]]:
        """Extract all facts from the XBRL document, grouped by concept name."""
        facts_by_concept: Dict[str, List[Dict[str, Any]]] = {}

        for fact in model_xbrl.facts:
            if fact.isNil or fact.value is None:
                continue

            concept_name = fact.qname.localName if fact.qname else None
            if not concept_name:
                continue

            # Get context information
            context = fact.context
            if context is None:
                continue

            # Parse dates
            period_end = None
            period_start = None
            instant = None

            if context.isInstantPeriod:
                instant = context.instantDatetime
                period_end = instant.date() if instant else None
            elif context.isStartEndPeriod:
                period_start = context.startDatetime.date() if context.startDatetime else None
                period_end = context.endDatetime.date() if context.endDatetime else None

            # Get dimensions (segment info)
            dimensions = {}
            if context.qnameDims:
                for dim_qname, dim_value in context.qnameDims.items():
                    dimensions[dim_qname.localName] = str(dim_value.memberQname.localName if dim_value.memberQname else dim_value)

            # Parse value
            # Note: XBRL values are the actual values. The decimals attribute indicates
            # precision, NOT a scaling factor. E.g., decimals="-3" means value is precise
            # to thousands, but the value itself is already correct.
            try:
                if fact.isNumeric:
                    value = float(fact.value.replace(",", "")) if fact.value else 0
                else:
                    value = fact.value
            except (ValueError, TypeError):
                value = fact.value

            # Get unit as clean string (USD, shares, etc.)
            unit_str = None
            if fact.unit:
                # Try to get clean unit string from measures
                if hasattr(fact.unit, 'measures') and fact.unit.measures:
                    measures = fact.unit.measures
                    if measures and len(measures) > 0 and len(measures[0]) > 0:
                        unit_str = measures[0][0].localName if hasattr(measures[0][0], 'localName') else str(measures[0][0])
                if not unit_str:
                    unit_str = "USD"  # Default to USD for monetary values

            # Ensure all values are JSON serializable
            decimals_str = str(fact.decimals) if fact.decimals is not None else None

            fact_data = {
                "value": value,
                "period_end": period_end,
                "period_start": period_start,
                "unit": unit_str,
                "dimensions": dimensions,
                "decimals": decimals_str,
            }

            if concept_name not in facts_by_concept:
                facts_by_concept[concept_name] = []
            facts_by_concept[concept_name].append(fact_data)

        return facts_by_concept

    def _extract_metadata(self, model_xbrl: ModelXbrl, facts: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
        """Extract filing metadata from XBRL document."""
        metadata = {
            "fiscal_year": None,
            "fiscal_period": None,
            "document_period_end": None,
            "currency": "USD",
        }

        # Try to find document period end date
        period_concepts = [
            "DocumentPeriodEndDate",
            "DocumentFiscalPeriodFocus",
            "DocumentFiscalYearFocus",
        ]

        for concept in period_concepts:
            if concept in facts and facts[concept]:
                fact = facts[concept][0]
                if concept == "DocumentPeriodEndDate":
                    if isinstance(fact["value"], date):
                        metadata["document_period_end"] = fact["value"]
                    elif isinstance(fact["value"], str):
                        # Parse string to date object
                        try:
                            metadata["document_period_end"] = datetime.strptime(fact["value"], "%Y-%m-%d").date()
                        except ValueError:
                            metadata["document_period_end"] = fact["value"]
                elif concept == "DocumentFiscalPeriodFocus":
                    metadata["fiscal_period"] = fact["value"]
                elif concept == "DocumentFiscalYearFocus":
                    try:
                        metadata["fiscal_year"] = int(fact["value"])
                    except (ValueError, TypeError):
                        pass

        return metadata

    def _map_to_statement(
        self,
        facts: Dict[str, List[Dict[str, Any]]],
        mappings: Dict[str, str],
        metadata: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Map XBRL facts to structured financial statement format."""
        result = {}
        period_end = metadata.get("document_period_end")

        for xbrl_tag, statement_path in mappings.items():
            if xbrl_tag not in facts:
                continue

            # Get the most relevant fact (prefer matching period, no dimensions)
            matching_facts = facts[xbrl_tag]
            best_fact = self._select_best_fact(matching_facts, period_end)

            if best_fact and best_fact["value"] is not None:
                # Get label for display
                label = STATEMENT_LABELS.get(statement_path, xbrl_tag)

                # Set the value in nested structure
                self._set_nested_value(result, statement_path, {
                    "label": label,
                    "value": best_fact["value"],
                    "unit": best_fact.get("unit", "USD"),
                })

        return result

    def _select_best_fact(
        self,
        facts: List[Dict[str, Any]],
        target_period: Optional[date],
    ) -> Optional[Dict[str, Any]]:
        """Select the best fact from a list based on period and dimensions."""
        if not facts:
            return None

        # Filter to facts without segment dimensions (consolidated view)
        no_dim_facts = [f for f in facts if not f.get("dimensions")]

        candidates = no_dim_facts if no_dim_facts else facts

        if not candidates:
            return None

        # If we have a target period, prefer facts matching that period
        if target_period:
            matching_period = [
                f for f in candidates
                if f.get("period_end") == target_period or f.get("instant") == target_period
            ]
            if matching_period:
                return matching_period[0]

        # Otherwise, return the most recent fact
        dated_facts = [f for f in candidates if f.get("period_end") or f.get("instant")]
        if dated_facts:
            dated_facts.sort(
                key=lambda x: x.get("period_end") or x.get("instant") or date.min,
                reverse=True,
            )
            return dated_facts[0]

        return candidates[0]

    def _set_nested_value(self, d: Dict, path: str, value: Any) -> None:
        """Set a value in a nested dictionary using dot notation path."""
        keys = path.split(".")
        current = d

        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]

        current[keys[-1]] = value

    # ========== NEW METHODS FOR FULL XBRL EXTRACTION ==========

    # Role URIs for identifying statement types
    STATEMENT_ROLE_PATTERNS = {
        "balance_sheet": ["StatementOfFinancialPosition", "BalanceSheet", "ConsolidatedBalanceSheet"],
        "income_statement": [
            "StatementOfIncome", "IncomeStatement", "StatementsOfOperations",
            "StatementOfOperations", "StatementsOfIncome", "ConsolidatedOperations",
            "ConsolidatedStatementsOfIncome", "StatementsOfConsolidatedIncome",
            "ComprehensiveIncome",  # Some companies combine income and comprehensive income
        ],
        "cash_flow": ["StatementOfCashFlows", "CashFlows", "StatementsOfCashFlows"],
        "equity_statement": ["StatementOfStockholdersEquity", "StockholdersEquity", "StatementOfEquity"],
    }

    def parse_filing_full(self, cik: int, accession_number: str, filing_date: Optional[date] = None) -> Dict[str, Any]:
        """
        Parse complete XBRL data from a filing including all facts, presentation hierarchy, and calculations.

        Returns a dict with:
        - all_facts: Dict of all facts keyed by concept name
        - presentation_trees: Dict of presentation trees per statement type
        - calculation_relationships: Dict of calculation relationships
        - labels: Dict of human-readable labels for concepts
        - metadata: Filing metadata (fiscal year, period, etc.)
        """
        xbrl_dir = self._get_xbrl_path(cik, accession_number, filing_date)
        if not xbrl_dir:
            raise FileNotFoundError(f"XBRL files not found for CIK {cik}, accession {accession_number}")

        xbrl_file = self._find_xbrl_file(xbrl_dir)
        if not xbrl_file:
            raise FileNotFoundError(f"No XBRL file found in {xbrl_dir}")

        logger.info(f"Parsing XBRL file (full): {xbrl_file}")

        try:
            # Load the XBRL document
            model_xbrl = self.model_manager.load(str(xbrl_file))

            if model_xbrl is None:
                raise ValueError("Failed to load XBRL document")

            # Extract all facts
            all_facts = self._extract_facts(model_xbrl)

            # Get metadata
            metadata = self._extract_metadata(model_xbrl, all_facts)

            # Extract human-readable labels
            labels = self._extract_all_labels(model_xbrl)

            # Extract presentation hierarchy
            presentation_trees = self._extract_presentation_hierarchy(model_xbrl, labels)

            # Extract calculation relationships
            calculation_relationships = self._extract_calculation_relationships(model_xbrl, labels)

            # Close the model
            self.model_manager.close()

            return {
                "all_facts": all_facts,
                "presentation_trees": presentation_trees,
                "calculation_relationships": calculation_relationships,
                "labels": labels,
                "metadata": metadata,
            }

        except Exception as e:
            logger.error(f"Error parsing XBRL (full): {e}")
            self.model_manager.close()
            raise

    def _extract_all_labels(self, model_xbrl: ModelXbrl) -> Dict[str, str]:
        """Extract human-readable labels for all concepts."""
        labels = {}

        try:
            # Get label relationship set
            label_rel_set = model_xbrl.relationshipSet("http://www.xbrl.org/2003/arcrole/concept-label")

            if label_rel_set:
                for rel in label_rel_set.modelRelationships:
                    concept = rel.fromModelObject
                    label_obj = rel.toModelObject

                    if concept and concept.qname and label_obj:
                        concept_name = concept.qname.localName
                        # Prefer standard or terse labels
                        label_role = getattr(label_obj, 'role', '') or ''
                        label_text = getattr(label_obj, 'text', '') or str(label_obj)

                        # Only store if we don't have one yet, or this is a better label
                        if concept_name not in labels:
                            labels[concept_name] = label_text
                        elif 'label' in label_role.lower() and 'terse' not in label_role.lower():
                            labels[concept_name] = label_text

            # Fallback: extract from model concepts
            if hasattr(model_xbrl, 'qnameConcepts'):
                for qname, concept in model_xbrl.qnameConcepts.items():
                    concept_name = qname.localName
                    if concept_name not in labels:
                        # Try to get label from concept
                        if hasattr(concept, 'label') and concept.label:
                            label_val = concept.label
                            # Ensure it's a string - might be an Arelle object
                            if hasattr(label_val, 'text'):
                                labels[concept_name] = str(label_val.text)
                            elif hasattr(label_val, 'stringValue'):
                                labels[concept_name] = str(label_val.stringValue)
                            elif isinstance(label_val, str):
                                labels[concept_name] = label_val
                            else:
                                labels[concept_name] = self._camel_to_title(concept_name)
                        else:
                            # Use concept name as fallback, with spaces inserted
                            labels[concept_name] = self._camel_to_title(concept_name)

        except Exception as e:
            logger.warning(f"Error extracting labels: {e}")

        return labels

    def _camel_to_title(self, name: str) -> str:
        """Convert CamelCase to Title Case with spaces."""
        import re
        # Insert space before uppercase letters
        spaced = re.sub(r'([a-z])([A-Z])', r'\1 \2', name)
        # Handle consecutive uppercase (e.g., USGovernment -> US Government)
        spaced = re.sub(r'([A-Z]+)([A-Z][a-z])', r'\1 \2', spaced)
        return spaced

    def _classify_role(self, role_uri: str) -> Optional[str]:
        """Classify a role URI into a statement type."""
        role_lower = role_uri.lower()
        for stmt_type, patterns in self.STATEMENT_ROLE_PATTERNS.items():
            for pattern in patterns:
                if pattern.lower() in role_lower:
                    return stmt_type
        return None

    def _extract_presentation_hierarchy(self, model_xbrl: ModelXbrl, labels: Dict[str, str]) -> Dict[str, Any]:
        """
        Extract presentation linkbase hierarchy organized by statement type.

        Returns dict with statement types as keys, each containing a list of
        PresentationNode trees in the authentic SEC filing order.
        """
        presentation_trees = {
            "balance_sheet": [],
            "income_statement": [],
            "cash_flow": [],
            "equity_statement": [],
            "other": [],
        }

        try:
            # Get presentation relationship set
            pre_rel_set = model_xbrl.relationshipSet("http://www.xbrl.org/2003/arcrole/parent-child")

            if not pre_rel_set or not pre_rel_set.modelRelationships:
                logger.warning("No presentation relationships found")
                return presentation_trees

            # Group relationships by role
            # Convert to list to avoid generator exhaustion
            all_relationships = list(pre_rel_set.modelRelationships)
            logger.info(f"Total relationships: {len(all_relationships)}")

            roles_seen = set()
            for rel in all_relationships:
                if hasattr(rel, 'linkrole'):
                    roles_seen.add(rel.linkrole)

            logger.info(f"Found {len(roles_seen)} roles in presentation linkbase")
            for r in list(roles_seen)[:5]:
                logger.info(f"  Role sample: {r}")

            # Debug: Check first few relationships for each role
            role_counts = {}
            for rel in all_relationships:
                r = getattr(rel, 'linkrole', None)
                if r:
                    role_counts[r] = role_counts.get(r, 0) + 1
            logger.info(f"  First 5 role counts: {list(role_counts.items())[:5]}")

            # Process each role
            for role_uri in roles_seen:
                stmt_type = self._classify_role(role_uri) or "other"

                # Find root concepts for this role (concepts that are "from" but not "to")
                from_concepts = set()
                to_concepts = set()

                # Use the pre-built list of relationships
                for rel in all_relationships:
                    rel_role = getattr(rel, 'linkrole', None)
                    if rel_role == role_uri:
                        # Use 'is not None' instead of truthiness for lxml elements
                        from_obj = rel.fromModelObject
                        to_obj = rel.toModelObject
                        from_qname = getattr(from_obj, 'qname', None) if from_obj is not None else None
                        to_qname = getattr(to_obj, 'qname', None) if to_obj is not None else None
                        if from_qname is not None:
                            from_concepts.add(from_qname.localName)
                        if to_qname is not None:
                            to_concepts.add(to_qname.localName)

                root_concepts = from_concepts - to_concepts

                # Only log for non-other statements with roots
                if root_concepts and stmt_type != "other":
                    logger.info(f"Role {role_uri[-60:]}: {len(root_concepts)} roots -> {stmt_type}")

                # Build tree for each root
                for root_name in sorted(root_concepts):
                    tree = self._build_presentation_tree(
                        all_relationships, root_name, role_uri, labels, level=0
                    )
                    if tree:
                        presentation_trees[stmt_type].append(tree)

        except Exception as e:
            logger.error(f"Error extracting presentation hierarchy: {e}")

        return presentation_trees

    def _build_presentation_tree(
        self,
        relationships: List,
        concept_name: str,
        role_uri: str,
        labels: Dict[str, str],
        level: int = 0,
        visited: Optional[set] = None
    ) -> Optional[Dict[str, Any]]:
        """Recursively build a presentation tree node."""
        if visited is None:
            visited = set()

        # Prevent infinite loops
        if concept_name in visited:
            return None
        visited.add(concept_name)

        # Find the concept object
        concept_obj = None
        is_abstract = False

        for rel in relationships:
            if getattr(rel, 'linkrole', None) == role_uri:
                # Use 'is not None' instead of truthiness for lxml elements
                from_obj = rel.fromModelObject
                to_obj = rel.toModelObject
                if from_obj is not None and getattr(from_obj, 'qname', None) is not None:
                    if from_obj.qname.localName == concept_name:
                        concept_obj = from_obj
                        break
                if to_obj is not None and getattr(to_obj, 'qname', None) is not None:
                    if to_obj.qname.localName == concept_name:
                        concept_obj = to_obj
                        break

        if concept_obj:
            is_abstract = getattr(concept_obj, 'isAbstract', False)

        # Get children
        children = []
        child_rels = []

        for rel in relationships:
            if getattr(rel, 'linkrole', None) != role_uri:
                continue
            # Use 'is not None' instead of truthiness for lxml elements
            from_obj = rel.fromModelObject
            to_obj = rel.toModelObject
            from_qname = getattr(from_obj, 'qname', None) if from_obj is not None else None
            to_qname = getattr(to_obj, 'qname', None) if to_obj is not None else None
            if from_qname is not None and from_qname.localName == concept_name:
                if to_qname is not None:
                    child_name = to_qname.localName
                    order = getattr(rel, 'order', 0) or 0
                    child_rels.append((order, child_name))

        # Sort children by order
        child_rels.sort(key=lambda x: x[0])

        for order, child_name in child_rels:
            child_tree = self._build_presentation_tree(
                relationships, child_name, role_uri, labels, level + 1, visited.copy()
            )
            if child_tree:
                children.append(child_tree)

        return {
            "concept": concept_name,
            "label": labels.get(concept_name, self._camel_to_title(concept_name)),
            "level": level,
            "is_abstract": is_abstract,
            "children": children,
        }

    def _extract_calculation_relationships(self, model_xbrl: ModelXbrl, labels: Dict[str, str]) -> Dict[str, Any]:
        """
        Extract calculation linkbase relationships showing how items roll up.

        Returns dict with parent concept names as keys, each containing a list
        of child relationships with weights.
        """
        calculations = {}

        try:
            # Get calculation relationship set
            calc_rel_set = model_xbrl.relationshipSet("http://www.xbrl.org/2003/arcrole/summation-item")

            if not calc_rel_set or not calc_rel_set.modelRelationships:
                logger.info("No calculation relationships found in linkbase")
                return calculations

            for rel in calc_rel_set.modelRelationships:
                # Use 'is None' instead of truthiness - lxml elements evaluate as False when empty
                if rel.fromModelObject is None or rel.toModelObject is None:
                    continue
                from_qname = getattr(rel.fromModelObject, 'qname', None)
                to_qname = getattr(rel.toModelObject, 'qname', None)
                if from_qname is None or to_qname is None:
                    continue

                parent_name = from_qname.localName
                child_name = to_qname.localName
                weight = getattr(rel, 'weight', 1.0) or 1.0
                order = getattr(rel, 'order', 0) or 0

                if parent_name not in calculations:
                    calculations[parent_name] = {
                        "parent_concept": parent_name,
                        "parent_label": labels.get(parent_name, self._camel_to_title(parent_name)),
                        "children": [],
                    }

                calculations[parent_name]["children"].append({
                    "concept": child_name,
                    "label": labels.get(child_name, self._camel_to_title(child_name)),
                    "weight": weight,
                    "order": order,
                })

            # Sort children by order
            for parent_name in calculations:
                calculations[parent_name]["children"].sort(key=lambda x: x["order"])

        except Exception as e:
            logger.error(f"Error extracting calculation relationships: {e}")

        return calculations
