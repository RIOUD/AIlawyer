#!/usr/bin/env python3
"""
Cross-Reference Manager for Legal Assistant

Manages cross-references between legal documents, identifies related concepts,
and provides relationship mapping for enhanced legal research.
"""

import os
import json
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
from datetime import datetime

from semantic_analyzer import SemanticAnalyzer
from database import LegalAssistantDB


class CrossReferenceManager:
    """
    Manages cross-references and relationships between legal documents.
    """
    
    def __init__(self, db_path: str = "./legal_assistant.db"):
        """
        Initialize the cross-reference manager.
        
        Args:
            db_path: Path to the database
        """
        self.semantic_analyzer = SemanticAnalyzer()
        self.db = LegalAssistantDB(db_path)
        self.cross_references_cache = {}
        self.relationships_cache = {}
    
    def build_semantic_index(self, vector_store_path: str = "./chroma_db"):
        """
        Build semantic index from existing vector store.
        
        Args:
            vector_store_path: Path to the ChromaDB vector store
        """
        try:
            from langchain_community.vectorstores import Chroma
            
            # Load existing vector store
            vector_store = Chroma(
                persist_directory=vector_store_path,
                embedding_function=None  # We'll use our own embeddings
            )
            
            # Get all documents
            collection = vector_store._collection
            results = collection.get()
            
            print(f"🔍 Building semantic index from {len(results['documents'])} documents...")
            
            # Process each document
            for i, (doc_id, document, metadata) in enumerate(zip(
                results['ids'], results['documents'], results['metadatas']
            )):
                # Add to semantic analyzer
                self.semantic_analyzer.add_document(
                    doc_id=doc_id,
                    content=document,
                    metadata=metadata or {}
                )
                
                if (i + 1) % 10 == 0:
                    print(f"   Processed {i + 1}/{len(results['documents'])} documents")
            
            print(f"✅ Semantic index built with {len(self.semantic_analyzer.document_embeddings)} documents")
            
        except Exception as e:
            print(f"❌ Error building semantic index: {e}")
    
    def find_cross_references(self, query: str, top_k: int = 5) -> Dict[str, Any]:
        """
        Find cross-references for a query.
        
        Args:
            query: Legal query
            top_k: Number of cross-references to return
            
        Returns:
            Dictionary with cross-reference information
        """
        # Find similar documents
        similar_docs = self.semantic_analyzer.find_similar_documents(query, top_k=top_k)
        
        # Find related concepts
        related_concepts = self.semantic_analyzer.find_related_concepts(query)
        
        # Find legal precedents
        precedents = self.semantic_analyzer.analyze_legal_precedents(query)
        
        # Suggest related questions
        related_questions = self.semantic_analyzer.suggest_related_questions(query)
        
        return {
            'query': query,
            'similar_documents': similar_docs,
            'related_concepts': related_concepts,
            'legal_precedents': precedents,
            'related_questions': related_questions,
            'timestamp': datetime.now().isoformat()
        }
    
    def get_document_relationships(self, doc_id: str) -> Dict[str, Any]:
        """
        Get comprehensive relationships for a specific document.
        
        Args:
            doc_id: Document identifier
            
        Returns:
            Dictionary with relationship information
        """
        if doc_id in self.relationships_cache:
            return self.relationships_cache[doc_id]
        
        relationships = self.semantic_analyzer.get_document_relationships(doc_id)
        self.relationships_cache[doc_id] = relationships
        return relationships
    
    def find_statute_regulation_links(self, query: str) -> List[Dict[str, Any]]:
        """
        Find links between statutes and regulations.
        
        Args:
            query: Legal query
            
        Returns:
            List of statute-regulation links
        """
        # Find documents related to the query
        similar_docs = self.semantic_analyzer.find_similar_documents(query, top_k=20)
        
        # Separate statutes and regulations
        statutes = []
        regulations = []
        
        for doc in similar_docs:
            doc_type = doc['metadata'].get('document_type', '')
            if doc_type == 'wetboeken':
                statutes.append(doc)
            elif doc_type in ['reglementering', 'advocatenstukken']:
                regulations.append(doc)
        
        # Find links between statutes and regulations
        links = []
        for statute in statutes:
            for regulation in regulations:
                # Check if they share concepts or jurisdiction
                statute_concepts = self.semantic_analyzer.extract_legal_concepts(
                    statute['metadata'].get('content', '')
                )
                regulation_concepts = self.semantic_analyzer.extract_legal_concepts(
                    regulation['metadata'].get('content', '')
                )
                
                common_concepts = set(statute_concepts) & set(regulation_concepts)
                
                if common_concepts or statute['metadata'].get('jurisdiction') == regulation['metadata'].get('jurisdiction'):
                    links.append({
                        'statute': statute,
                        'regulation': regulation,
                        'common_concepts': list(common_concepts),
                        'relationship_type': 'statute_regulation_link'
                    })
        
        return links
    
    def analyze_legal_network(self, query: str) -> Dict[str, Any]:
        """
        Analyze the legal network around a query.
        
        Args:
            query: Legal query
            
        Returns:
            Dictionary with network analysis
        """
        # Get cross-references
        cross_refs = self.find_cross_references(query)
        
        # Find statute-regulation links
        statute_links = self.find_statute_regulation_links(query)
        
        # Analyze concept relationships
        concepts = self.semantic_analyzer.extract_legal_concepts(query)
        concept_network = {}
        
        for concept in concepts:
            if concept in self.semantic_analyzer.concept_embeddings:
                related_docs = self.semantic_analyzer.concept_embeddings[concept]
                concept_network[concept] = {
                    'document_count': len(related_docs),
                    'documents': related_docs[:5],  # Top 5 documents
                    'related_concepts': self.semantic_analyzer.find_related_concepts(concept)
                }
        
        return {
            'query': query,
            'cross_references': cross_refs,
            'statute_regulation_links': statute_links,
            'concept_network': concept_network,
            'network_summary': {
                'total_documents': len(cross_refs['similar_documents']),
                'total_concepts': len(concepts),
                'total_precedents': len(cross_refs['legal_precedents']),
                'total_links': len(statute_links)
            }
        }
    
    def suggest_research_path(self, query: str) -> Dict[str, Any]:
        """
        Suggest a research path for a legal query.
        
        Args:
            query: Legal query
            
        Returns:
            Dictionary with research path suggestions
        """
        # Extract concepts
        concepts = self.semantic_analyzer.extract_legal_concepts(query)
        
        # Find relevant precedents
        precedents = self.semantic_analyzer.analyze_legal_precedents(query)
        
        # Find related statutes
        similar_docs = self.semantic_analyzer.find_similar_documents(query, top_k=10)
        statutes = [doc for doc in similar_docs if doc['metadata'].get('document_type') == 'wetboeken']
        
        # Find related regulations
        regulations = [doc for doc in similar_docs if doc['metadata'].get('document_type') == 'reglementering']
        
        # Suggest research steps
        research_steps = []
        
        if precedents:
            research_steps.append({
                'step': 1,
                'type': 'precedents',
                'description': 'Review relevant legal precedents',
                'documents': precedents[:3],
                'reasoning': 'Precedents provide interpretation of the law'
            })
        
        if statutes:
            research_steps.append({
                'step': 2,
                'type': 'statutes',
                'description': 'Examine applicable statutes and codes',
                'documents': statutes[:3],
                'reasoning': 'Statutes establish the legal framework'
            })
        
        if regulations:
            research_steps.append({
                'step': 3,
                'type': 'regulations',
                'description': 'Check implementing regulations',
                'documents': regulations[:3],
                'reasoning': 'Regulations provide detailed implementation'
            })
        
        # Add concept-based research
        if concepts:
            research_steps.append({
                'step': len(research_steps) + 1,
                'type': 'concepts',
                'description': 'Explore related legal concepts',
                'concepts': concepts,
                'reasoning': 'Related concepts provide broader context'
            })
        
        return {
            'query': query,
            'research_steps': research_steps,
            'estimated_complexity': self._estimate_research_complexity(query, concepts, precedents),
            'suggested_approach': self._suggest_research_approach(concepts, precedents)
        }
    
    def _estimate_research_complexity(self, query: str, concepts: List[str], precedents: List[Dict]) -> str:
        """
        Estimate the complexity of research needed.
        
        Args:
            query: Legal query
            concepts: Identified legal concepts
            precedents: Relevant precedents
            
        Returns:
            Complexity level (Low, Medium, High)
        """
        complexity_score = 0
        
        # More concepts = higher complexity
        complexity_score += len(concepts) * 2
        
        # More precedents = higher complexity
        complexity_score += len(precedents)
        
        # Query length indicates complexity
        complexity_score += len(query.split()) // 5
        
        if complexity_score <= 3:
            return "Low"
        elif complexity_score <= 7:
            return "Medium"
        else:
            return "High"
    
    def _suggest_research_approach(self, concepts: List[str], precedents: List[Dict]) -> str:
        """
        Suggest a research approach based on available information.
        
        Args:
            concepts: Identified legal concepts
            precedents: Relevant precedents
            
        Returns:
            Suggested approach description
        """
        if len(precedents) > 5:
            return "Start with recent precedents and work backwards to establish legal evolution"
        elif len(concepts) > 3:
            return "Focus on primary concepts first, then explore related areas"
        elif precedents:
            return "Begin with precedents to understand current interpretation"
        else:
            return "Start with statutory framework and build understanding systematically"
    
    def export_cross_references(self, query: str, output_path: str) -> bool:
        """
        Export cross-reference analysis to JSON.
        
        Args:
            query: Legal query
            output_path: Output file path
            
        Returns:
            True if export successful
        """
        try:
            # Get comprehensive analysis
            analysis = self.analyze_legal_network(query)
            research_path = self.suggest_research_path(query)
            
            export_data = {
                'query': query,
                'timestamp': datetime.now().isoformat(),
                'cross_reference_analysis': analysis,
                'research_path': research_path,
                'summary': {
                    'total_documents_found': len(analysis['cross_references']['similar_documents']),
                    'total_precedents': len(analysis['cross_references']['legal_precedents']),
                    'total_concepts': len(analysis['cross_references']['related_concepts']),
                    'research_complexity': research_path['estimated_complexity']
                }
            }
            
            # Write to file
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            return True
            
        except Exception as e:
            print(f"❌ Error exporting cross-references: {e}")
            return False
    
    def get_cross_reference_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about cross-references.
        
        Args:
            Dictionary with cross-reference statistics
        """
        total_documents = len(self.semantic_analyzer.document_embeddings)
        total_concepts = len(self.semantic_analyzer.concept_embeddings)
        
        # Calculate concept distribution
        concept_distribution = {}
        for concept, doc_ids in self.semantic_analyzer.concept_embeddings.items():
            concept_distribution[concept] = len(doc_ids)
        
        # Find most connected documents
        document_connections = {}
        for doc_id in self.semantic_analyzer.document_embeddings:
            cross_refs = self.semantic_analyzer.find_cross_references(doc_id, top_k=100)
            document_connections[doc_id] = len(cross_refs)
        
        most_connected = sorted(document_connections.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            'total_documents': total_documents,
            'total_concepts': total_concepts,
            'concept_distribution': concept_distribution,
            'most_connected_documents': most_connected,
            'average_connections_per_document': sum(document_connections.values()) / len(document_connections) if document_connections else 0
        } 