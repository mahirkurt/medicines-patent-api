"""
Cortellis Patent & Drug Data Processing System
Standardizes and processes Cortellis data for database integration
"""
import pandas as pd
import json
import os
import sys
from datetime import datetime
import hashlib
import re

# Set UTF-8 encoding
sys.stdout.reconfigure(encoding='utf-8')

class CortellisDataProcessor:
    def __init__(self):
        self.patents_file = 'cortellis_patents.xlsx'
        self.drugs_file = 'cortellis_drugs.xlsx'
        self.output_dir = 'processed_data'

        # Create output directory
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def clean_text(self, text):
        """Clean and standardize text data"""
        if pd.isna(text):
            return None
        text = str(text).strip()
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        return text if text else None

    def parse_date(self, date_str):
        """Parse and standardize date formats"""
        if pd.isna(date_str):
            return None
        try:
            if isinstance(date_str, pd.Timestamp):
                return date_str.strftime('%Y-%m-%d')
            return pd.to_datetime(date_str).strftime('%Y-%m-%d')
        except:
            return str(date_str)

    def parse_list_field(self, field):
        """Parse semicolon-separated fields into lists"""
        if pd.isna(field):
            return []
        items = str(field).split(';')
        return [item.strip() for item in items if item.strip()]

    def generate_id(self, *args):
        """Generate unique ID from multiple fields"""
        content = '|'.join(str(arg) for arg in args if arg)
        return hashlib.md5(content.encode()).hexdigest()[:16]

    def process_patents(self):
        """Process and standardize patent data"""
        print("\n🔬 PROCESSING PATENT DATA...")
        print("-" * 50)

        # Read the main patent data
        df = pd.read_excel(self.patents_file, sheet_name='Birlestirilmis_Veri')
        print(f"Total patents: {len(df)}")

        patents = []
        for idx, row in df.iterrows():
            if idx % 5000 == 0:
                print(f"  Processing patent {idx}/{len(df)}...")

            # Extract and structure patent data
            patent = {
                'id': self.generate_id(row.get('patent_number'), row.get('application_number')),
                'patent_number': self.clean_text(row.get('patent_number')),
                'application_number': self.clean_text(row.get('application_number')),
                'title': self.clean_text(row.get('invention_title')),
                'abstract': self.clean_text(row.get('annotation')),
                'classifications': self.parse_list_field(row.get('abstract_classification')),
                'advantages': self.clean_text(row.get('advantage')),
                'application_date': self.parse_date(row.get('application_date')),
                'grant_date': self.parse_date(row.get('grant_date')),
                'expiry_date': self.parse_date(row.get('earliest_expiry_date')),
                'latest_expiry_date': self.parse_date(row.get('latest_expiry_date')),
                'inventors': self.parse_list_field(row.get('inventor_name')),
                'grantees': self.parse_list_field(row.get('grantee')),
                'original_applicants': self.parse_list_field(row.get('original_applicant')),
                'compound_name': self.clean_text(row.get('compound_name')),
                'drugs': self.parse_list_field(row.get('drugs')),
                'chemistry': self.clean_text(row.get('chemistry')),
                'biology': self.clean_text(row.get('biology')),
                'formulation': self.clean_text(row.get('formulation')),
                'jurisdiction': self.clean_text(row.get('jurisdiction')),
                'medical_uses': self.parse_list_field(row.get('medical_use')),
                'targets': self.parse_list_field(row.get('target')),
                'mechanisms': self.parse_list_field(row.get('mechanism')),
                'pharmacokinetics': self.clean_text(row.get('pharmacokinetics')),
                'patent_family': self.clean_text(row.get('patent_family')),
                'data_source': 'Cortellis',
                'processed_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }

            # Remove None values and empty lists
            patent = {k: v for k, v in patent.items() if v is not None and v != [] and v != ''}
            patents.append(patent)

        # Save processed patents
        output_file = os.path.join(self.output_dir, 'patents_processed.json')
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(patents, f, ensure_ascii=False, indent=2)

        print(f"✅ Processed {len(patents)} patents")
        print(f"   Saved to: {output_file}")

        # Generate statistics
        self.generate_patent_stats(patents)

        return patents

    def process_drugs(self):
        """Process and standardize drug data"""
        print("\n💊 PROCESSING DRUG DATA...")
        print("-" * 50)

        # Read the main drug data
        df = pd.read_excel(self.drugs_file, sheet_name='Birlestirilmis_Veri')
        print(f"Total drugs: {len(df)}")

        drugs = []
        for idx, row in df.iterrows():
            if idx % 1000 == 0:
                print(f"  Processing drug {idx}/{len(df)}...")

            # Extract and structure drug data
            drug = {
                'id': self.clean_text(row.get('drug_id')),
                'name': self.clean_text(row.get('drug_name')),
                'synonyms': self.parse_list_field(row.get('synonyms')),
                'active_companies': self.parse_list_field(row.get('active_companies')),
                'inactive_companies': self.parse_list_field(row.get('inactive_companies')),
                'active_indications': self.parse_list_field(row.get('active_indications')),
                'inactive_indications': self.parse_list_field(row.get('inactive_indications')),
                'highest_phase': self.clean_text(row.get('highest_phase_overall')),
                'mechanism_of_action': self.parse_list_field(row.get('mechanism')),
                'targets': self.parse_list_field(row.get('target')),
                'therapeutic_class': self.parse_list_field(row.get('therapeutic_class')),
                'ephmra_codes': self.parse_list_field(row.get('ephmra_codes')),
                'first_launched_date': self.parse_date(row.get('first_launched_date')),
                'first_launched_country': self.clean_text(row.get('first_launched_country/territory')),
                'first_launched_indication': self.clean_text(row.get('first_launched_indication')),
                'last_updated': self.parse_date(row.get('last_updated_date')),
                'added_date': self.parse_date(row.get('added_date')),
                'summary': self.clean_text(row.get('first_paragraph_of_summary')),
                'phases': {
                    'launched': self.clean_text(row.get('phases_launched')),
                    'phase_3': self.clean_text(row.get('phases_phase_3')),
                    'phase_2': self.clean_text(row.get('phases_phase_2')),
                    'phase_1': self.clean_text(row.get('phases_phase_1')),
                    'preclinical': self.clean_text(row.get('phases_preclinical'))
                },
                'data_source': 'Cortellis',
                'processed_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }

            # Clean phases dictionary
            drug['phases'] = {k: v for k, v in drug['phases'].items() if v}
            if not drug['phases']:
                del drug['phases']

            # Remove None values and empty lists
            drug = {k: v for k, v in drug.items() if v is not None and v != [] and v != ''}
            drugs.append(drug)

        # Save processed drugs
        output_file = os.path.join(self.output_dir, 'drugs_processed.json')
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(drugs, f, ensure_ascii=False, indent=2)

        print(f"✅ Processed {len(drugs)} drugs")
        print(f"   Saved to: {output_file}")

        # Generate statistics
        self.generate_drug_stats(drugs)

        return drugs

    def generate_patent_stats(self, patents):
        """Generate patent statistics"""
        stats = {
            'total_patents': len(patents),
            'patents_with_drugs': len([p for p in patents if 'drugs' in p]),
            'unique_compounds': len(set(p.get('compound_name', '') for p in patents if p.get('compound_name'))),
            'unique_grantees': len(set(g for p in patents for g in p.get('grantees', []))),
            'classification_distribution': {},
            'year_distribution': {}
        }

        # Classification distribution
        all_classifications = []
        for patent in patents:
            all_classifications.extend(patent.get('classifications', []))

        for cls in set(all_classifications):
            stats['classification_distribution'][cls] = all_classifications.count(cls)

        # Year distribution
        for patent in patents:
            if 'application_date' in patent:
                year = patent['application_date'][:4] if patent['application_date'] else 'Unknown'
                stats['year_distribution'][year] = stats['year_distribution'].get(year, 0) + 1

        # Save statistics
        stats_file = os.path.join(self.output_dir, 'patent_statistics.json')
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(stats, f, ensure_ascii=False, indent=2)

        print(f"\n📊 Patent Statistics:")
        print(f"   Total Patents: {stats['total_patents']}")
        print(f"   Patents with Drugs: {stats['patents_with_drugs']}")
        print(f"   Unique Compounds: {stats['unique_compounds']}")
        print(f"   Unique Grantees: {stats['unique_grantees']}")

    def generate_drug_stats(self, drugs):
        """Generate drug statistics"""
        stats = {
            'total_drugs': len(drugs),
            'launched_drugs': len([d for d in drugs if d.get('highest_phase') == 'Launched']),
            'phase_distribution': {},
            'indication_distribution': {},
            'company_distribution': {}
        }

        # Phase distribution
        for drug in drugs:
            phase = drug.get('highest_phase', 'Unknown')
            stats['phase_distribution'][phase] = stats['phase_distribution'].get(phase, 0) + 1

        # Indication distribution (top 20)
        all_indications = []
        for drug in drugs:
            all_indications.extend(drug.get('active_indications', []))

        indication_counts = {}
        for ind in all_indications:
            indication_counts[ind] = indication_counts.get(ind, 0) + 1

        stats['indication_distribution'] = dict(
            sorted(indication_counts.items(), key=lambda x: x[1], reverse=True)[:20]
        )

        # Company distribution (top 20)
        all_companies = []
        for drug in drugs:
            all_companies.extend(drug.get('active_companies', []))

        company_counts = {}
        for company in all_companies:
            company_counts[company] = company_counts.get(company, 0) + 1

        stats['company_distribution'] = dict(
            sorted(company_counts.items(), key=lambda x: x[1], reverse=True)[:20]
        )

        # Save statistics
        stats_file = os.path.join(self.output_dir, 'drug_statistics.json')
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(stats, f, ensure_ascii=False, indent=2)

        print(f"\n📊 Drug Statistics:")
        print(f"   Total Drugs: {stats['total_drugs']}")
        print(f"   Launched Drugs: {stats['launched_drugs']}")
        print(f"   Phase Distribution: {stats['phase_distribution']}")

    def create_relationships(self, patents, drugs):
        """Create relationships between patents and drugs"""
        print("\n🔗 CREATING RELATIONSHIPS...")
        print("-" * 50)

        relationships = []

        # Drug-Patent relationships
        drug_dict = {drug['name'].lower(): drug for drug in drugs if 'name' in drug}

        for patent in patents:
            patent_drugs = patent.get('drugs', [])
            for drug_name in patent_drugs:
                drug_name_lower = drug_name.lower()
                if drug_name_lower in drug_dict:
                    relationship = {
                        'type': 'drug_patent',
                        'drug_id': drug_dict[drug_name_lower].get('id'),
                        'drug_name': drug_name,
                        'patent_id': patent.get('id'),
                        'patent_number': patent.get('patent_number'),
                        'relationship_date': patent.get('application_date')
                    }
                    relationships.append(relationship)

        # Save relationships
        rel_file = os.path.join(self.output_dir, 'relationships.json')
        with open(rel_file, 'w', encoding='utf-8') as f:
            json.dump(relationships, f, ensure_ascii=False, indent=2)

        print(f"✅ Created {len(relationships)} relationships")

        return relationships

    def process_all(self):
        """Process all Cortellis data"""
        print("\n" + "=" * 80)
        print("CORTELLIS DATA PROCESSING SYSTEM")
        print("=" * 80)

        # Process patents and drugs
        patents = self.process_patents()
        drugs = self.process_drugs()

        # Create relationships
        relationships = self.create_relationships(patents, drugs)

        # Create master index
        master_index = {
            'metadata': {
                'source': 'Cortellis',
                'processed_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'version': '1.0'
            },
            'statistics': {
                'total_patents': len(patents),
                'total_drugs': len(drugs),
                'total_relationships': len(relationships)
            },
            'files': {
                'patents': 'patents_processed.json',
                'drugs': 'drugs_processed.json',
                'relationships': 'relationships.json',
                'patent_stats': 'patent_statistics.json',
                'drug_stats': 'drug_statistics.json'
            }
        }

        index_file = os.path.join(self.output_dir, 'master_index.json')
        with open(index_file, 'w', encoding='utf-8') as f:
            json.dump(master_index, f, ensure_ascii=False, indent=2)

        print("\n" + "=" * 80)
        print("✅ PROCESSING COMPLETE!")
        print(f"   Output directory: {self.output_dir}")
        print(f"   Master index: {index_file}")
        print("=" * 80)

if __name__ == "__main__":
    processor = CortellisDataProcessor()
    processor.process_all()