#!/usr/bin/env python3
"""
Template Manager for Legal Assistant

Manages legal document templates, custom template uploads, and document generation.
"""

import os
import json
import shutil
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from datetime import datetime

from template_library import TemplateLibrary


class TemplateManager:
    """
    Manages legal document templates and document generation.
    """
    
    def __init__(self, templates_dir: str = "./templates", custom_dir: str = "./custom_templates"):
        """
        Initialize the template manager.
        
        Args:
            templates_dir: Directory for built-in templates
            custom_dir: Directory for custom templates
        """
        self.template_library = TemplateLibrary()
        self.templates_dir = Path(templates_dir)
        self.custom_dir = Path(custom_dir)
        
        # Create directories if they don't exist
        self.templates_dir.mkdir(exist_ok=True)
        self.custom_dir.mkdir(exist_ok=True)
        
        # Load custom templates
        self.custom_templates = self._load_custom_templates()
    
    def _load_custom_templates(self) -> Dict[str, Any]:
        """
        Load custom templates from the custom templates directory.
        
        Returns:
            Dictionary of custom templates
        """
        custom_templates = {}
        
        if not self.custom_dir.exists():
            return custom_templates
        
        for template_file in self.custom_dir.glob("*.json"):
            try:
                with open(template_file, 'r', encoding='utf-8') as f:
                    template_data = json.load(f)
                    category = template_data.get('category', 'custom')
                    template_id = template_data.get('template_id', template_file.stem)
                    
                    if category not in custom_templates:
                        custom_templates[category] = {}
                    
                    custom_templates[category][template_id] = template_data
            except Exception as e:
                print(f"Warning: Could not load custom template {template_file}: {e}")
        
        return custom_templates
    
    def get_template(self, category: str, template_id: str, use_custom: bool = True) -> Optional[Dict[str, Any]]:
        """
        Get a template by category and ID.
        
        Args:
            category: Template category
            template_id: Template identifier
            use_custom: Whether to include custom templates
            
        Returns:
            Template dictionary or None if not found
        """
        # First check custom templates
        if use_custom and category in self.custom_templates:
            custom_template = self.custom_templates[category].get(template_id)
            if custom_template:
                return custom_template
        
        # Then check built-in templates
        return self.template_library.get_template(category, template_id)
    
    def list_all_templates(self, include_custom: bool = True) -> Dict[str, Any]:
        """
        List all available templates.
        
        Args:
            include_custom: Whether to include custom templates
            
        Returns:
            Dictionary of all templates
        """
        all_templates = self.template_library.list_templates()
        
        if include_custom:
            for category, templates in self.custom_templates.items():
                if category not in all_templates:
                    all_templates[category] = {}
                all_templates[category].update(templates)
        
        return all_templates
    
    def search_templates(self, query: str, include_custom: bool = True) -> List[Dict[str, Any]]:
        """
        Search templates by name or description.
        
        Args:
            query: Search query
            include_custom: Whether to include custom templates
            
        Returns:
            List of matching templates
        """
        results = self.template_library.search_templates(query)
        
        if include_custom:
            query_lower = query.lower()
            for category, templates in self.custom_templates.items():
                for template_id, template in templates.items():
                    if (query_lower in template['name'].lower() or 
                        query_lower in template['description'].lower()):
                        results.append({
                            'category': category,
                            'template_id': template_id,
                            'template': template,
                            'is_custom': True
                        })
        
        return results
    
    def generate_document(self, category: str, template_id: str, 
                         variables: Dict[str, str], use_custom: bool = True) -> Dict[str, Any]:
        """
        Generate a document from a template.
        
        Args:
            category: Template category
            template_id: Template identifier
            variables: Template variables
            use_custom: Whether to use custom templates
            
        Returns:
            Dictionary with generated document and metadata
        """
        template = self.get_template(category, template_id, use_custom)
        if not template:
            return {'error': 'Template not found'}
        
        # Validate variables
        validation = self.template_library.validate_template_variables(
            template_id, category, variables
        )
        
        if not validation['valid']:
            return {
                'error': 'Invalid variables',
                'missing_variables': validation['missing_variables'],
                'extra_variables': validation['extra_variables']
            }
        
        try:
            # Generate document
            template_text = template['template']
            generated_document = template_text.format(**variables)
            
            return {
                'success': True,
                'document': generated_document,
                'template_info': {
                    'name': template['name'],
                    'description': template['description'],
                    'language': template.get('language', 'unknown'),
                    'jurisdiction': template.get('jurisdiction', 'unknown'),
                    'category': category,
                    'template_id': template_id,
                    'is_custom': category in self.custom_templates
                },
                'variables_used': variables,
                'generated_at': datetime.now().isoformat()
            }
        
        except Exception as e:
            return {'error': f'Error generating document: {e}'}
    
    def upload_custom_template(self, template_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Upload a custom template.
        
        Args:
            template_data: Template data dictionary
            
        Returns:
            Upload result
        """
        try:
            # Validate required fields
            required_fields = ['name', 'description', 'template', 'variables', 'category']
            for field in required_fields:
                if field not in template_data:
                    return {'error': f'Missing required field: {field}'}
            
            # Generate template ID if not provided
            if 'template_id' not in template_data:
                template_data['template_id'] = self._generate_template_id(template_data['name'])
            
            # Add metadata
            template_data['uploaded_at'] = datetime.now().isoformat()
            template_data['is_custom'] = True
            
            # Save template file
            category = template_data['category']
            template_id = template_data['template_id']
            
            # Create category directory if it doesn't exist
            category_dir = self.custom_dir / category
            category_dir.mkdir(exist_ok=True)
            
            template_file = category_dir / f"{template_id}.json"
            
            with open(template_file, 'w', encoding='utf-8') as f:
                json.dump(template_data, f, indent=2, ensure_ascii=False)
            
            # Update custom templates
            if category not in self.custom_templates:
                self.custom_templates[category] = {}
            
            self.custom_templates[category][template_id] = template_data
            
            return {
                'success': True,
                'template_id': template_id,
                'category': category,
                'file_path': str(template_file)
            }
        
        except Exception as e:
            return {'error': f'Error uploading template: {e}'}
    
    def _generate_template_id(self, name: str) -> str:
        """
        Generate a template ID from a name.
        
        Args:
            name: Template name
            
        Returns:
            Generated template ID
        """
        # Convert to lowercase and replace spaces with underscores
        template_id = name.lower().replace(' ', '_').replace('-', '_')
        
        # Remove special characters
        template_id = ''.join(c for c in template_id if c.isalnum() or c == '_')
        
        # Add timestamp to ensure uniqueness
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        template_id = f"{template_id}_{timestamp}"
        
        return template_id
    
    def delete_custom_template(self, category: str, template_id: str) -> Dict[str, Any]:
        """
        Delete a custom template.
        
        Args:
            category: Template category
            template_id: Template identifier
            
        Returns:
            Deletion result
        """
        try:
            if category not in self.custom_templates:
                return {'error': 'Category not found'}
            
            if template_id not in self.custom_templates[category]:
                return {'error': 'Template not found'}
            
            # Remove from memory
            del self.custom_templates[category][template_id]
            
            # Remove empty category
            if not self.custom_templates[category]:
                del self.custom_templates[category]
            
            # Delete file
            template_file = self.custom_dir / category / f"{template_id}.json"
            if template_file.exists():
                template_file.unlink()
            
            return {'success': True, 'message': 'Template deleted successfully'}
        
        except Exception as e:
            return {'error': f'Error deleting template: {e}'}
    
    def export_template(self, category: str, template_id: str, 
                       output_path: str, use_custom: bool = True) -> Dict[str, Any]:
        """
        Export a template to a file.
        
        Args:
            category: Template category
            template_id: Template identifier
            output_path: Output file path
            use_custom: Whether to include custom templates
            
        Returns:
            Export result
        """
        template = self.get_template(category, template_id, use_custom)
        if not template:
            return {'error': 'Template not found'}
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(template, f, indent=2, ensure_ascii=False)
            
            return {'success': True, 'output_path': output_path}
        
        except Exception as e:
            return {'error': f'Error exporting template: {e}'}
    
    def import_template(self, template_file_path: str) -> Dict[str, Any]:
        """
        Import a template from a file.
        
        Args:
            template_file_path: Path to template file
            
        Returns:
            Import result
        """
        try:
            with open(template_file_path, 'r', encoding='utf-8') as f:
                template_data = json.load(f)
            
            return self.upload_custom_template(template_data)
        
        except Exception as e:
            return {'error': f'Error importing template: {e}'}
    
    def get_template_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about templates.
        
        Returns:
            Template statistics
        """
        # Built-in templates
        built_in_templates = self.template_library.list_templates()
        built_in_count = sum(len(templates) for templates in built_in_templates.values())
        
        # Custom templates
        custom_count = sum(len(templates) for templates in self.custom_templates.values())
        
        # Language distribution
        language_dist = {}
        jurisdiction_dist = {}
        
        # Count built-in templates
        for category, templates in built_in_templates.items():
            for template in templates.values():
                lang = template.get('language', 'unknown')
                jurisdiction = template.get('jurisdiction', 'unknown')
                
                language_dist[lang] = language_dist.get(lang, 0) + 1
                jurisdiction_dist[jurisdiction] = jurisdiction_dist.get(jurisdiction, 0) + 1
        
        # Count custom templates
        for category, templates in self.custom_templates.items():
            for template in templates.values():
                lang = template.get('language', 'unknown')
                jurisdiction = template.get('jurisdiction', 'unknown')
                
                language_dist[lang] = language_dist.get(lang, 0) + 1
                jurisdiction_dist[jurisdiction] = jurisdiction_dist.get(jurisdiction, 0) + 1
        
        return {
            'total_templates': built_in_count + custom_count,
            'built_in_templates': built_in_count,
            'custom_templates': custom_count,
            'categories': list(built_in_templates.keys()) + list(self.custom_templates.keys()),
            'language_distribution': language_dist,
            'jurisdiction_distribution': jurisdiction_dist
        }
    
    def backup_templates(self, backup_path: str) -> Dict[str, Any]:
        """
        Backup all custom templates.
        
        Args:
            backup_path: Backup directory path
            
        Returns:
            Backup result
        """
        try:
            backup_dir = Path(backup_path)
            backup_dir.mkdir(exist_ok=True)
            
            # Copy custom templates directory
            if self.custom_dir.exists():
                backup_custom_dir = backup_dir / "custom_templates"
                shutil.copytree(self.custom_dir, backup_custom_dir, dirs_exist_ok=True)
            
            # Create metadata file
            metadata = {
                'backup_date': datetime.now().isoformat(),
                'statistics': self.get_template_statistics(),
                'template_categories': self.template_library.get_template_categories()
            }
            
            metadata_file = backup_dir / "backup_metadata.json"
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            
            return {
                'success': True,
                'backup_path': str(backup_dir),
                'metadata_file': str(metadata_file)
            }
        
        except Exception as e:
            return {'error': f'Error backing up templates: {e}'}
    
    def restore_templates(self, backup_path: str) -> Dict[str, Any]:
        """
        Restore templates from backup.
        
        Args:
            backup_path: Backup directory path
            
        Returns:
            Restore result
        """
        try:
            backup_dir = Path(backup_path)
            if not backup_dir.exists():
                return {'error': 'Backup directory not found'}
            
            # Restore custom templates
            backup_custom_dir = backup_dir / "custom_templates"
            if backup_custom_dir.exists():
                if self.custom_dir.exists():
                    shutil.rmtree(self.custom_dir)
                shutil.copytree(backup_custom_dir, self.custom_dir)
                
                # Reload custom templates
                self.custom_templates = self._load_custom_templates()
            
            return {
                'success': True,
                'restored_templates': len(self.custom_templates)
            }
        
        except Exception as e:
            return {'error': f'Error restoring templates: {e}'} 