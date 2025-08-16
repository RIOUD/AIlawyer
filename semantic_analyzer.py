#!/usr/bin/env python3
"""
Semantic Analyzer for Cross-Reference Detection

Performs semantic similarity analysis on legal documents to identify
related concepts, precedents, and cross-references.
"""

import numpy as np
from typing import List, Dict, Any, Tuple, Optional
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
import json
import re
from collections import defaultdict

from config import EMBEDDING_MODEL_NAME


class SemanticAnalyzer:
    """
    Analyzes legal documents for semantic similarity and cross-references.
    """
    
    def __init__(self, model_name: str = EMBEDDING_MODEL_NAME):
        """
        Initialize the semantic analyzer.
        
        Args:
            model_name: Name of the sentence transformer model to use
        """
        self.model = SentenceTransformer(model_name)
        self.document_embeddings = {}
        self.document_metadata = {}
        self.concept_embeddings = {}
        
        # Legal concept patterns for Belgian law
        self.legal_concepts = {
            "arbeidsovereenkomst": [
                "arbeidsovereenkomst", "werkgever", "werknemer", "arbeidscontract",
                "loon", "werkuren", "opzegtermijn", "ontslag", "arbeidsrecht"
            ],
            "eigendom": [
                "eigendom", "eigenaar", "bezit", "eigendomsrecht", "onroerend goed",
                "roerend goed", "hypotheek", "pandrecht", "vruchtgebruik"
            ],
            "aansprakelijkheid": [
                "aansprakelijkheid", "schade", "vergoeding", "fout", "causaal verband",
                "schadevergoeding", "burgerlijke aansprakelijkheid", "contractuele aansprakelijkheid"
            ],
            "handel": [
                "handel", "handelsactiviteit", "vergunning", "handelsregister",
                "vennootschap", "onderneming", "handelsrecht", "commerciële activiteit"
            ],
            "privacy": [
                "privacy", "persoonsgegevens", "bescherming", "verwerking", "toestemming",
                "gegevensbescherming", "AVG", "GDPR", "privacyrecht"
            ],
            "procesrecht": [
                "procesrecht", "dagvaarding", "conclusie", "vonnis", "arrest",
                "rechtbank", "hof", "beroep", "cassatie", "executie"
            ]
        }
    
    def extract_legal_concepts(self, text: str) -> List[str]:
        """
        Extract legal concepts from text.
        
        Args:
            text: Text to analyze
            
        Returns:
            List of identified legal concepts
        """
        text_lower = text.lower()
        found_concepts = []
        
        for concept, keywords in self.legal_concepts.items():
            for keyword in keywords:
                if keyword in text_lower:
                    found_concepts.append(concept)
                    break
        
        return list(set(found_concepts))
    
    def create_document_embedding(self, content: str, metadata: Dict[str, Any]) -> np.ndarray:
        """
        Create embedding for a document.
        
        Args:
            content: Document content
            metadata: Document metadata
            
        Returns:
            Document embedding vector
        """
        # Combine content with metadata for richer representation
        combined_text = f"{content} {metadata.get('document_type', '')} {metadata.get('jurisdiction', '')}"
        
        # Create embedding
        embedding = self.model.encode(combined_text)
        return embedding
    
    def add_document(self, doc_id: str, content: str, metadata: Dict[str, Any]):
        """
        Add a document to the semantic analyzer.
        
        Args:
            doc_id: Unique document identifier
            content: Document content
            metadata: Document metadata
        """
        # Create embedding
        embedding = self.create_document_embedding(content, metadata)
        self.document_embeddings[doc_id] = embedding
        self.document_metadata[doc_id] = metadata
        
        # Extract and store legal concepts
        concepts = self.extract_legal_concepts(content)
        if concepts:
            for concept in concepts:
                if concept not in self.concept_embeddings:
                    self.concept_embeddings[concept] = []
                self.concept_embeddings[concept].append(doc_id)
    
    def find_similar_documents(self, query: str, top_k: int = 5, 
                              threshold: float = 0.7) -> List[Dict[str, Any]]:
        """
        Find documents similar to a query.
        
        Args:
            query: Query text
            top_k: Number of similar documents to return
            threshold: Similarity threshold
            
        Returns:
            List of similar documents with similarity scores
        """
        if not self.document_embeddings:
            return []
        
        # Create query embedding
        query_embedding = self.model.encode(query)
        
        # Calculate similarities
        similarities = []
        for doc_id, doc_embedding in self.document_embeddings.items():
            similarity = cosine_similarity([query_embedding], [doc_embedding])[0][0]
            if similarity >= threshold:
                similarities.append({
                    'doc_id': doc_id,
                    'similarity': similarity,
                    'metadata': self.document_metadata[doc_id]
                })
        
        # Sort by similarity and return top_k
        similarities.sort(key=lambda x: x['similarity'], reverse=True)
        return similarities[:top_k]
    
    def find_related_concepts(self, query: str) -> List[str]:
        """
        Find legal concepts related to a query.
        
        Args:
            query: Query text
            
        Returns:
            List of related legal concepts
        """
        query_concepts = self.extract_legal_concepts(query)
        related_concepts = set(query_concepts)
        
        # Find concepts that frequently co-occur
        for concept in query_concepts:
            if concept in self.concept_embeddings:
                related_docs = self.concept_embeddings[concept]
                for doc_id in related_docs:
                    if doc_id in self.document_metadata:
                        doc_concepts = self.extract_legal_concepts(
                            self.document_metadata[doc_id].get('content', '')
                        )
                        related_concepts.update(doc_concepts)
        
        return list(related_concepts - set(query_concepts))
    
    def find_cross_references(self, doc_id: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Find cross-references for a specific document.
        
        Args:
            doc_id: Document identifier
            top_k: Number of cross-references to return
            
        Returns:
            List of cross-referenced documents
        """
        if doc_id not in self.document_embeddings:
            return []
        
        doc_embedding = self.document_embeddings[doc_id]
        doc_metadata = self.document_metadata[doc_id]
        
        # Find similar documents
        similarities = []
        for other_id, other_embedding in self.document_embeddings.items():
            if other_id != doc_id:
                similarity = cosine_similarity([doc_embedding], [other_embedding])[0][0]
                similarities.append({
                    'doc_id': other_id,
                    'similarity': similarity,
                    'metadata': self.document_metadata[other_id],
                    'relationship_type': self._determine_relationship_type(
                        doc_metadata, self.document_metadata[other_id]
                    )
                })
        
        # Sort by similarity and return top_k
        similarities.sort(key=lambda x: x['similarity'], reverse=True)
        return similarities[:top_k]
    
    def _determine_relationship_type(self, doc1_meta: Dict, doc2_meta: Dict) -> str:
        """
        Determine the type of relationship between two documents.
        
        Args:
            doc1_meta: First document metadata
            doc2_meta: Second document metadata
            
        Returns:
            Relationship type description
        """
        # Same document type
        if doc1_meta.get('document_type') == doc2_meta.get('document_type'):
            return f"Same document type: {doc1_meta.get('document_type')}"
        
        # Same jurisdiction
        if doc1_meta.get('jurisdiction') == doc2_meta.get('jurisdiction'):
            return f"Same jurisdiction: {doc1_meta.get('jurisdiction')}"
        
        # Related by date
        doc1_date = doc1_meta.get('date', '')
        doc2_date = doc2_meta.get('date', '')
        if doc1_date and doc2_date and doc1_date == doc2_date:
            return f"Same year: {doc1_date}"
        
        # Related by concept
        doc1_concepts = self.extract_legal_concepts(doc1_meta.get('content', ''))
        doc2_concepts = self.extract_legal_concepts(doc2_meta.get('content', ''))
        common_concepts = set(doc1_concepts) & set(doc2_concepts)
        if common_concepts:
            return f"Related concepts: {', '.join(common_concepts)}"
        
        return "Semantically similar"
    
    def suggest_related_questions(self, query: str, top_k: int = 3) -> List[str]:
        """
        Suggest related questions based on a query.
        
        Args:
            query: Original query
            top_k: Number of suggestions to return
            
        Returns:
            List of suggested related questions
        """
        # Extract concepts from query
        concepts = self.extract_legal_concepts(query)
        
        # Generate question templates based on concepts
        question_templates = {
            "arbeidsovereenkomst": [
                "Wat zijn de rechten van een werknemer bij een arbeidsovereenkomst?",
                "Hoe kan een arbeidsovereenkomst worden opgezegd?",
                "Welke verplichtingen heeft een werkgever?",
                "Wat zijn de gevolgen van een onrechtmatige opzegging?"
            ],
            "eigendom": [
                "Hoe wordt eigendom gedefinieerd volgens het Burgerlijk Wetboek?",
                "Wat zijn de rechten van een eigenaar?",
                "Hoe kan eigendom worden overgedragen?",
                "Wat zijn de beperkingen van eigendomsrecht?"
            ],
            "aansprakelijkheid": [
                "Wanneer is er sprake van aansprakelijkheid?",
                "Welke soorten schadevergoeding zijn er?",
                "Hoe wordt causaliteit bewezen?",
                "Wat zijn de verjaringstermijnen voor schadevorderingen?"
            ],
            "handel": [
                "Welke vergunningen zijn nodig voor handelsactiviteiten?",
                "Hoe wordt een vennootschap opgericht?",
                "Wat zijn de verplichtingen van een handelaar?",
                "Hoe wordt handelsrecht gehandhaafd?"
            ],
            "privacy": [
                "Welke rechten hebben betrokkenen onder de AVG?",
                "Wanneer is verwerking van persoonsgegevens toegestaan?",
                "Wat zijn de verplichtingen van een verwerkingsverantwoordelijke?",
                "Hoe wordt privacyrecht gehandhaafd?"
            ],
            "procesrecht": [
                "Hoe wordt een rechtszaak aangespannen?",
                "Wat zijn de termijnen in het procesrecht?",
                "Hoe werkt het beroepssysteem?",
                "Wat zijn de kosten van een rechtszaak?"
            ]
        }
        
        suggestions = []
        for concept in concepts:
            if concept in question_templates:
                suggestions.extend(question_templates[concept])
        
        # Remove duplicates and return top_k
        unique_suggestions = list(set(suggestions))
        return unique_suggestions[:top_k]
    
    def get_document_relationships(self, doc_id: str) -> Dict[str, Any]:
        """
        Get comprehensive relationship information for a document.
        
        Args:
            doc_id: Document identifier
            
        Returns:
            Dictionary with relationship information
        """
        if doc_id not in self.document_metadata:
            return {}
        
        metadata = self.document_metadata[doc_id]
        content = metadata.get('content', '')
        
        # Extract concepts
        concepts = self.extract_legal_concepts(content)
        
        # Find related documents
        cross_refs = self.find_cross_references(doc_id)
        
        # Find documents with same concepts
        concept_docs = []
        for concept in concepts:
            if concept in self.concept_embeddings:
                for related_doc_id in self.concept_embeddings[concept]:
                    if related_doc_id != doc_id:
                        concept_docs.append({
                            'doc_id': related_doc_id,
                            'concept': concept,
                            'metadata': self.document_metadata[related_doc_id]
                        })
        
        return {
            'document_id': doc_id,
            'concepts': concepts,
            'cross_references': cross_refs,
            'concept_related_documents': concept_docs,
            'jurisdiction': metadata.get('jurisdiction'),
            'document_type': metadata.get('document_type'),
            'date': metadata.get('date')
        }
    
    def analyze_legal_precedents(self, query: str) -> List[Dict[str, Any]]:
        """
        Analyze and find relevant legal precedents for a query.
        
        Args:
            query: Legal query
            
        Returns:
            List of relevant precedents with analysis
        """
        # Find similar documents
        similar_docs = self.find_similar_documents(query, top_k=10)
        
        # Filter for jurisprudence
        precedents = []
        for doc in similar_docs:
            if doc['metadata'].get('document_type') == 'jurisprudentie':
                precedents.append({
                    'doc_id': doc['doc_id'],
                    'similarity': doc['similarity'],
                    'metadata': doc['metadata'],
                    'relevance': self._analyze_precedent_relevance(query, doc['metadata'])
                })
        
        # Sort by relevance
        precedents.sort(key=lambda x: x['relevance'], reverse=True)
        return precedents
    
    def _analyze_precedent_relevance(self, query: str, precedent_metadata: Dict) -> float:
        """
        Analyze the relevance of a precedent to a query.
        
        Args:
            query: Legal query
            precedent_metadata: Precedent metadata
            
        Returns:
            Relevance score (0-1)
        """
        # Extract concepts from query and precedent
        query_concepts = self.extract_legal_concepts(query)
        precedent_concepts = self.extract_legal_concepts(precedent_metadata.get('content', ''))
        
        # Calculate concept overlap
        if not query_concepts or not precedent_concepts:
            return 0.0
        
        overlap = len(set(query_concepts) & set(precedent_concepts))
        total_concepts = len(set(query_concepts) | set(precedent_concepts))
        
        if total_concepts == 0:
            return 0.0
        
        return overlap / total_concepts 