import os
import json
import shutil
from pathlib import Path
from typing import Dict

class Config:
    """Manages configuration and project setup."""
    
    DOMAIN_TEMPLATES = {
        'cpg': {
            'description': 'Consumer Packaged Goods - Retail and consumer products data',
            'bronze_schema': 'RAW_DATA',
            'silver_schema': 'CURATED_DATA',
            'icon': '🛒',
            'example_mappings': [
                {
                    'source': 'vendor_master',
                    'target': 'dim_supplier_master',
                    'transformations': ['rename_columns', 'data_quality_checks']
                },
                {
                    'source': 'product_master',
                    'target': 'dim_product',
                    'transformations': ['rename_columns', 'standardize_codes']
                },
                {
                    'source': 'sales_data',
                    'target': 'fact_sales',
                    'transformations': ['rename_columns', 'aggregate_metrics']
                },
                {
                    'source': 'customer_data',
                    'target': 'dim_customer',
                    'transformations': ['rename_columns', 'deduplicate']
                }
            ]
        },
        'bfsi': {
            'description': 'Banking & Financial Services - Financial transactions and banking data',
            'bronze_schema': 'RAW_DATA',
            'silver_schema': 'CURATED_DATA',
            'icon': '🏦',
            'example_mappings': [
                {
                    'source': 'raw_global_incoterms',
                    'target': 'dim_global_incoterms',
                    'transformations': ['rename_columns', 'standardize_codes', 'data_quality_checks'],
                    'columns': [
                        'inc_surrogate_key', 'incoterm_cd', 'incoterm_description', 
                        'inc_version', 'delivery_grp', 'seller_duties', 'buyer_duties',
                        'risk_xfer_pt', 'cost_xfer_pt', 'transport_modes', 'insurance_party',
                        'export_clear_party', 'import_clear_party', 'loading_party',
                        'unload_party', 'container_suitable', 'bulk_suitable',
                        'doc_requirements', 'usage_scenarios', 'risk_level',
                        'status_ind', 'created_by_user', 'creation_date'
                    ]
                },
                {
                    'source': 'raw_document_tracking',
                    'target': 'fact_document_tracking',
                    'transformations': ['rename_columns', 'data_quality_checks', 'type_casting'],
                    'columns': [
                        'doc_track_id', 'trade_transaction_id', 'doc_type_code',
                        'submission_date', 'doc_ref_num', 'doc_date_str', 'doc_issuer_name',
                        'doc_value_amount', 'document_currency', 'quantity_shipped',
                        'unit_of_measure', 'unit_price', 'vessel_name', 'voyage_number',
                        'bl_date', 'shipment_date', 'doc_status_code', 'verification_date',
                        'verified_by', 'discrepancy_details', 'waiver_requested'
                    ]
                }
            ]
        },
        'hospital': {
            'description': 'Healthcare Management - Medical and healthcare data systems',
            'bronze_schema': 'RAW_DATA',
            'silver_schema': 'CURATED_DATA',
            'icon': '🏥',
            'example_mappings': [
                {
                    'source': 'patient_master',
                    'target': 'dim_patient',
                    'transformations': ['rename_columns', 'data_quality_checks', 'phi_masking']
                }
            ]
        }
    }
    
    @staticmethod
    def get_template_dir() -> Path:
        """Get the templates directory."""
        return Path(__file__).parent / 'templates'
    
    @staticmethod
    def create_project_structure(install_path: Path) -> None:
        """Create necessary directories."""
        directories = ['backend', 'frontend', 'data', 'config']
        
        for directory in directories:
            (install_path / directory).mkdir(parents=True, exist_ok=True)
    
    @staticmethod
    def copy_templates(install_path: Path) -> None:
        """Copy template files and directories to installation directory."""
        template_dir = Config.get_template_dir()
        
        # Copy docker-compose.yml
        shutil.copy2(
            template_dir / 'docker-compose.yml',
            install_path / 'docker-compose.yml'
        )
        
        # Copy config.json if exists
        if (template_dir / 'config.json').exists():
            shutil.copy2(
                template_dir / 'config.json',
                install_path / 'config.json'
            )
        
        # Copy Dockerfiles
        shutil.copy2(
            template_dir / 'backend-Dockerfile',
            install_path / 'backend' / 'Dockerfile'
        )
        
        shutil.copy2(
            template_dir / 'frontend-Dockerfile',
            install_path / 'frontend' / 'Dockerfile'
        )
        
        # Copy backend files
        backend_src = Path(__file__).parent.parent / 'backend'
        if backend_src.exists():
            for item in ['main.py', 'requirements.txt', 'transformation_functions.py']:
                src_file = backend_src / item
                if src_file.exists():
                    shutil.copy2(src_file, install_path / 'backend' / item)
        
        # Copy frontend files
        frontend_src = Path(__file__).parent.parent / 'frontend'
        if frontend_src.exists():
            for item in ['package.json', 'nginx.conf']:
                src_file = frontend_src / item
                if src_file.exists():
                    shutil.copy2(src_file, install_path / 'frontend' / item)
            
            # Copy directories
            for dir_name in ['src', 'public']:
                src_dir = frontend_src / dir_name
                dst_dir = install_path / 'frontend' / dir_name
                if src_dir.exists():
                    shutil.copytree(src_dir, dst_dir, dirs_exist_ok=True)
    
    @staticmethod
    def create_env_file(install_path: Path) -> None:
        """Create .env file from template."""
        template_dir = Config.get_template_dir()
        env_example = template_dir / '.env.example'
        env_file = install_path / '.env'
        
        if env_example.exists() and not env_file.exists():
            shutil.copy2(env_example, env_file)
    
    @staticmethod
    def create_domain_config(install_path: Path, domain: str) -> None:
        """Create domain-specific configuration file."""
        config_file = install_path / 'domain-config.json'
        
        if domain == 'custom':
            config_data = {
                'domain': 'custom',
                'description': 'Custom domain configuration',
                'bronze_schema': 'RAW_DATA',
                'silver_schema': 'CURATED_DATA',
                'example_mappings': []
            }
        else:
            template = Config.DOMAIN_TEMPLATES.get(domain, Config.DOMAIN_TEMPLATES['cpg'])
            config_data = {
                'domain': domain,
                **template
            }
        
        with open(config_file, 'w') as f:
            json.dump(config_data, f, indent=2)
    
    @staticmethod
    def setup_domain_templates(install_path: Path, domain: str) -> None:
        """Setup domain-specific template files and examples."""
        config_dir = install_path / 'config'
        config_dir.mkdir(exist_ok=True)
        
        # Create a README for the domain
        readme_path = config_dir / f'{domain}_README.md'
        
        domain_info = Config.DOMAIN_TEMPLATES.get(domain, {})
        
        readme_content = f"""# {domain.upper()} Domain Configuration

## Description
{domain_info.get('description', 'Domain-specific transformations')}

## Schema Configuration
- **Bronze Layer**: {domain_info.get('bronze_schema', 'RAW_DATA')}
- **Silver Layer**: {domain_info.get('silver_schema', 'CURATED_DATA')}

## Example Mappings

"""
        
        for mapping in domain_info.get('example_mappings', []):
            readme_content += f"""### {mapping['source']} → {mapping['target']}
**Source Table**: `{mapping['source']}`
**Target Table**: `{mapping['target']}`
**Transformations**: {', '.join(mapping['transformations'])}

"""
        
        readme_content += """
## Getting Started

1. Review the example mappings above
2. Create your pipelines in the UI (http://localhost:3000)
3. Execute transformations Bronze → Silver

## Custom Transformations

You can add custom transformation logic in the UI by:
- Renaming columns
- Adding derived columns
- Joining with other tables
- Applying data quality rules
"""
        
        with open(readme_path, 'w') as f:
            f.write(readme_content)