"""
Google Patents Integration System using SerpAPI
Fetches and integrates patent data from Google Patents
"""
import os
import sys
import json
import time
import hashlib
from datetime import datetime
from typing import Dict, List, Optional
import requests
from urllib.parse import quote

# Set UTF-8 encoding
sys.stdout.reconfigure(encoding='utf-8')

class GooglePatentsAPI:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://serpapi.com/search"
        self.cache_dir = "cache/google_patents"

        # Create cache directory
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)

    def search_patents(self, query: str, num_results: int = 100) -> List[Dict]:
        """
        Search Google Patents using SerpAPI
        """
        print(f"\n🔍 Searching Google Patents for: {query}")

        all_results = []
        offset = 0

        while len(all_results) < num_results:
            # Check cache first
            cache_key = f"{query}_{offset}_{num_results}"
            cache_file = os.path.join(self.cache_dir, f"{hashlib.md5(cache_key.encode()).hexdigest()}.json")

            if os.path.exists(cache_file):
                # Load from cache if less than 24 hours old
                cache_age = time.time() - os.path.getmtime(cache_file)
                if cache_age < 86400:  # 24 hours
                    print(f"  Loading from cache (offset={offset})...")
                    with open(cache_file, 'r', encoding='utf-8') as f:
                        cached_data = json.load(f)
                        all_results.extend(cached_data.get('patents', []))
                        offset += 10
                        continue

            # Make API request
            params = {
                'engine': 'google_patents',
                'q': query,
                'api_key': self.api_key,
                'start': offset,
                'num': min(10, num_results - len(all_results))  # Google Patents returns max 10 per request
            }

            print(f"  Fetching results (offset={offset})...")

            try:
                response = requests.get(self.base_url, params=params, timeout=30)
                response.raise_for_status()
                data = response.json()

                # Extract patent results
                patents = data.get('organic_results', [])

                if not patents:
                    print(f"  No more results found.")
                    break

                # Process and standardize patent data
                processed_patents = []
                for patent in patents:
                    processed_patent = self._process_patent_result(patent)
                    processed_patents.append(processed_patent)

                all_results.extend(processed_patents)

                # Cache the results
                with open(cache_file, 'w', encoding='utf-8') as f:
                    json.dump({'patents': processed_patents, 'timestamp': datetime.now().isoformat()}, f)

                print(f"  Found {len(processed_patents)} patents (total: {len(all_results)})")

                # Rate limiting
                time.sleep(1)

                offset += 10

            except requests.exceptions.RequestException as e:
                print(f"  ⚠️ API request failed: {e}")
                break
            except Exception as e:
                print(f"  ⚠️ Error processing results: {e}")
                break

        return all_results[:num_results]

    def get_patent_details(self, patent_id: str) -> Optional[Dict]:
        """
        Get detailed information for a specific patent
        """
        print(f"\n📄 Fetching details for patent: {patent_id}")

        # Check cache
        cache_file = os.path.join(self.cache_dir, f"detail_{patent_id}.json")
        if os.path.exists(cache_file):
            cache_age = time.time() - os.path.getmtime(cache_file)
            if cache_age < 86400:  # 24 hours
                print(f"  Loading from cache...")
                with open(cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)

        params = {
            'engine': 'google_patents',
            'q': patent_id,
            'api_key': self.api_key
        }

        try:
            response = requests.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()

            # Process the detailed result
            if data.get('organic_results'):
                detailed_patent = self._process_patent_detail(data['organic_results'][0])

                # Cache the result
                with open(cache_file, 'w', encoding='utf-8') as f:
                    json.dump(detailed_patent, f, ensure_ascii=False, indent=2)

                return detailed_patent

        except Exception as e:
            print(f"  ⚠️ Failed to fetch patent details: {e}")

        return None

    def _process_patent_result(self, patent: Dict) -> Dict:
        """
        Process and standardize patent search result
        """
        return {
            'id': patent.get('patent_id', ''),
            'title': patent.get('title', ''),
            'snippet': patent.get('snippet', ''),
            'publication_date': patent.get('publication_date', ''),
            'filing_date': patent.get('filing_date', ''),
            'grant_date': patent.get('grant_date', ''),
            'inventors': patent.get('inventors', []),
            'assignee': patent.get('assignee', ''),
            'patent_type': patent.get('type', ''),
            'pdf_link': patent.get('pdf', ''),
            'google_patents_link': patent.get('link', ''),
            'priority_date': patent.get('priority_date', ''),
            'application_number': patent.get('application_number', ''),
            'data_source': 'Google Patents',
            'fetched_date': datetime.now().isoformat()
        }

    def _process_patent_detail(self, patent: Dict) -> Dict:
        """
        Process detailed patent information
        """
        return {
            'id': patent.get('patent_id', ''),
            'title': patent.get('title', ''),
            'abstract': patent.get('abstract', ''),
            'description': patent.get('description', ''),
            'claims': patent.get('claims', []),
            'publication_date': patent.get('publication_date', ''),
            'filing_date': patent.get('filing_date', ''),
            'grant_date': patent.get('grant_date', ''),
            'priority_date': patent.get('priority_date', ''),
            'inventors': patent.get('inventors', []),
            'assignee': patent.get('assignee', ''),
            'current_assignee': patent.get('current_assignee', ''),
            'classifications': {
                'ipc': patent.get('ipc_classifications', []),
                'cpc': patent.get('cpc_classifications', []),
                'us': patent.get('us_classifications', [])
            },
            'cited_by': patent.get('cited_by', []),
            'citations': patent.get('citations', []),
            'similar_patents': patent.get('similar_documents', []),
            'legal_events': patent.get('legal_events', []),
            'patent_family': patent.get('patent_family', []),
            'pdf_link': patent.get('pdf', ''),
            'google_patents_link': patent.get('link', ''),
            'images': patent.get('images', []),
            'data_source': 'Google Patents',
            'fetched_date': datetime.now().isoformat()
        }

    def search_pharmaceutical_patents(self, drug_names: List[str], indications: List[str] = None) -> Dict:
        """
        Search for pharmaceutical-related patents
        """
        print("\n" + "=" * 80)
        print("PHARMACEUTICAL PATENT SEARCH")
        print("=" * 80)

        all_patents = {}

        # Search by drug names
        for drug_name in drug_names[:10]:  # Limit to first 10 for demo
            print(f"\n🔬 Searching patents for drug: {drug_name}")

            # Search queries
            queries = [
                f'"{drug_name}" pharmaceutical',
                f'"{drug_name}" formulation',
                f'"{drug_name}" composition',
                f'"{drug_name}" method treatment'
            ]

            drug_patents = []
            for query in queries:
                results = self.search_patents(query, num_results=10)
                drug_patents.extend(results)

            # Remove duplicates
            unique_patents = {}
            for patent in drug_patents:
                unique_patents[patent['id']] = patent

            all_patents[drug_name] = list(unique_patents.values())
            print(f"  Found {len(unique_patents)} unique patents for {drug_name}")

            # Rate limiting
            time.sleep(2)

        # Search by indications if provided
        if indications:
            for indication in indications[:5]:  # Limit to first 5 for demo
                print(f"\n🏥 Searching patents for indication: {indication}")

                query = f'"{indication}" treatment method pharmaceutical'
                results = self.search_patents(query, num_results=20)

                all_patents[f"indication_{indication}"] = results
                print(f"  Found {len(results)} patents for {indication}")

                time.sleep(2)

        return all_patents


class PatentDataMerger:
    """
    Merges Cortellis and Google Patents data
    """
    def __init__(self):
        self.cortellis_dir = "processed_data"
        self.output_dir = "unified_patent_data"

        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def merge_patent_data(self, cortellis_patents: List[Dict], google_patents: Dict) -> List[Dict]:
        """
        Merge Cortellis and Google Patents data
        """
        print("\n🔗 MERGING PATENT DATA...")
        print("-" * 50)

        merged_patents = []

        # Create lookup dictionaries
        cortellis_by_number = {}
        for patent in cortellis_patents:
            if patent.get('patent_number'):
                cortellis_by_number[patent['patent_number']] = patent
            if patent.get('application_number'):
                cortellis_by_number[patent['application_number']] = patent

        # Process Google Patents
        google_patent_list = []
        for category, patents in google_patents.items():
            for patent in patents:
                patent['search_category'] = category
                google_patent_list.append(patent)

        # Merge matching patents
        matched_count = 0
        for google_patent in google_patent_list:
            patent_id = google_patent.get('id', '')
            app_number = google_patent.get('application_number', '')

            merged_patent = google_patent.copy()

            # Check if we have matching Cortellis data
            cortellis_match = None
            if patent_id in cortellis_by_number:
                cortellis_match = cortellis_by_number[patent_id]
            elif app_number in cortellis_by_number:
                cortellis_match = cortellis_by_number[app_number]

            if cortellis_match:
                # Merge data from both sources
                merged_patent['data_sources'] = ['Cortellis', 'Google Patents']
                merged_patent['cortellis_data'] = {
                    'compound_name': cortellis_match.get('compound_name'),
                    'drugs': cortellis_match.get('drugs', []),
                    'medical_uses': cortellis_match.get('medical_uses', []),
                    'targets': cortellis_match.get('targets', []),
                    'mechanisms': cortellis_match.get('mechanisms', []),
                    'advantages': cortellis_match.get('advantages'),
                    'biology': cortellis_match.get('biology'),
                    'chemistry': cortellis_match.get('chemistry'),
                    'formulation': cortellis_match.get('formulation')
                }
                matched_count += 1
            else:
                merged_patent['data_sources'] = ['Google Patents']

            merged_patents.append(merged_patent)

        # Add Cortellis-only patents
        for patent_number, cortellis_patent in cortellis_by_number.items():
            # Check if already merged
            already_merged = any(
                p.get('id') == patent_number or
                p.get('application_number') == patent_number
                for p in merged_patents
            )

            if not already_merged:
                merged_patent = cortellis_patent.copy()
                merged_patent['data_sources'] = ['Cortellis']
                merged_patents.append(merged_patent)

        print(f"✅ Merged {len(merged_patents)} total patents")
        print(f"   Matched: {matched_count}")
        print(f"   Cortellis only: {len(cortellis_by_number) - matched_count}")
        print(f"   Google only: {len(google_patent_list) - matched_count}")

        return merged_patents

    def save_unified_data(self, merged_patents: List[Dict], merged_drugs: List[Dict]):
        """
        Save unified patent and drug data
        """
        print("\n💾 SAVING UNIFIED DATA...")
        print("-" * 50)

        # Save merged patents
        patents_file = os.path.join(self.output_dir, 'unified_patents.json')
        with open(patents_file, 'w', encoding='utf-8') as f:
            json.dump(merged_patents, f, ensure_ascii=False, indent=2)
        print(f"   Saved patents to: {patents_file}")

        # Save merged drugs (from Cortellis)
        drugs_file = os.path.join(self.output_dir, 'unified_drugs.json')
        with open(drugs_file, 'w', encoding='utf-8') as f:
            json.dump(merged_drugs, f, ensure_ascii=False, indent=2)
        print(f"   Saved drugs to: {drugs_file}")

        # Create master index
        master_index = {
            'metadata': {
                'sources': ['Cortellis', 'Google Patents'],
                'processed_date': datetime.now().isoformat(),
                'version': '2.0'
            },
            'statistics': {
                'total_patents': len(merged_patents),
                'total_drugs': len(merged_drugs),
                'data_sources': {
                    'cortellis_only': len([p for p in merged_patents if p.get('data_sources') == ['Cortellis']]),
                    'google_only': len([p for p in merged_patents if p.get('data_sources') == ['Google Patents']]),
                    'both': len([p for p in merged_patents if len(p.get('data_sources', [])) > 1])
                }
            },
            'files': {
                'patents': 'unified_patents.json',
                'drugs': 'unified_drugs.json'
            }
        }

        index_file = os.path.join(self.output_dir, 'master_index.json')
        with open(index_file, 'w', encoding='utf-8') as f:
            json.dump(master_index, f, ensure_ascii=False, indent=2)
        print(f"   Saved master index to: {index_file}")

        print("\n✅ Unified data saved successfully!")


def main():
    """
    Main execution function
    """
    print("\n" + "=" * 80)
    print("PATENT DATA INTEGRATION SYSTEM")
    print("=" * 80)

    # Initialize Google Patents API
    api_key = "20860d94b3b1f4f197f2aa79c0cf7bb0b429431cb97a5257a53b5070068ac455"
    google_api = GooglePatentsAPI(api_key)

    # Load processed Cortellis data if available
    cortellis_patents = []
    cortellis_drugs = []

    if os.path.exists('processed_data/patents_processed.json'):
        print("\n📂 Loading Cortellis data...")
        with open('processed_data/patents_processed.json', 'r', encoding='utf-8') as f:
            cortellis_patents = json.load(f)
        print(f"   Loaded {len(cortellis_patents)} Cortellis patents")

        with open('processed_data/drugs_processed.json', 'r', encoding='utf-8') as f:
            cortellis_drugs = json.load(f)
        print(f"   Loaded {len(cortellis_drugs)} Cortellis drugs")

    # Extract drug names for Google Patents search
    drug_names = []
    for drug in cortellis_drugs[:20]:  # Limit for demo
        if drug.get('name'):
            drug_names.append(drug['name'])

    # Extract common indications
    indication_counts = {}
    for drug in cortellis_drugs:
        for indication in drug.get('active_indications', []):
            indication_counts[indication] = indication_counts.get(indication, 0) + 1

    top_indications = sorted(indication_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    indications = [ind[0] for ind in top_indications]

    print(f"\n🔍 Searching Google Patents for:")
    print(f"   Top drugs: {drug_names[:5]}")
    print(f"   Top indications: {indications}")

    # Search Google Patents
    google_patents = google_api.search_pharmaceutical_patents(drug_names, indications)

    # Initialize merger
    merger = PatentDataMerger()

    # Merge data
    merged_patents = merger.merge_patent_data(cortellis_patents, google_patents)

    # Save unified data
    merger.save_unified_data(merged_patents, cortellis_drugs)

    print("\n" + "=" * 80)
    print("✅ INTEGRATION COMPLETE!")
    print("=" * 80)


if __name__ == "__main__":
    main()