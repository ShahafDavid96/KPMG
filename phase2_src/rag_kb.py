"""
Simple RAG Knowledge Base - Exactly 3 chunks per file (18 total)
Uses embeddings for vector search with minimal memory footprint
"""

import logging
import re
import gc
from pathlib import Path
from typing import Dict, Any, List, Optional
import numpy as np
import faiss
import time

logger = logging.getLogger(__name__)


class RAGKB:
    """RAG-based knowledge base with exactly 3 chunks per file"""
    
    def __init__(self, use_azure_embeddings=True):
        """Initialize simple RAG KB
        
        Args:
            use_azure_embeddings: Whether to use Azure OpenAI embeddings
        """
        self.chunks = []
        self.embeddings = []
        self.faiss_index = None
        self.azure_client = None
        self.data_dir = Path(__file__).parent.parent / "phase2_data"
        
        # Initialize Azure client if needed
        if use_azure_embeddings:
            self._init_azure_client()
        
        # Load and process data (exactly 18 chunks)
        self._load_and_process_data()
    
    def _init_azure_client(self):
        """Initialize Azure OpenAI client"""
        try:
            from config import get_azure_client
            self.azure_client = get_azure_client()
            if self.azure_client:
                logger.info("Azure OpenAI client initialized")
            else:
                logger.warning("Azure OpenAI client not available")
        except Exception as e:
            logger.warning(f"Could not initialize Azure OpenAI client: {e}")
            self.azure_client = None
    
    def _load_and_process_data(self):
        """Load and process data with exactly 3 chunks per file"""
        try:
            html_files = list(self.data_dir.glob("*.html"))
            if not html_files:
                logger.warning("No HTML files found")
                return
            
            logger.info(f"Processing {len(html_files)} HTML files with 3 chunks each")
            
            for html_file in html_files:
                try:
                    # Create exactly 3 chunks for this file
                    file_chunks = self._create_three_chunks(html_file)
                    self.chunks.extend(file_chunks)
                    
                    logger.info(f"Created {len(file_chunks)} chunks for {html_file.name}")
                    
                except Exception as e:
                    logger.error(f"Error processing {html_file}: {e}")
                    continue
            
            logger.info(f"Total chunks created: {len(self.chunks)} (target: 18)")
            
            # Create embeddings for all chunks
            if self.chunks:
                self._create_embeddings()
                self._build_faiss_index()
                logger.info("RAG system ready with embeddings!")
            
        except Exception as e:
            logger.error(f"Error in data processing: {e}")
    
    def _create_three_chunks(self, html_file: Path) -> List[Dict[str, Any]]:
        """Create exactly 3 chunks per file - one for each HMO"""
        try:
            service_name = html_file.stem
            
            # Read file content
            with open(html_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Clean HTML
            clean_content = self._clean_html(content)
            
            # Create 3 HMO-specific chunks
            chunks = []
            
            # Chunk 1: Maccabi (מכבי) services and coverage
            maccabi_chunk = self._extract_hmo_chunk(clean_content, service_name, 'maccabi', 'מכבי')
            chunks.append(maccabi_chunk)
            
            # Chunk 2: Meuhedet (מאוחדת) services and coverage
            meuhedet_chunk = self._extract_hmo_chunk(clean_content, service_name, 'meuhedet', 'מאוחדת')
            chunks.append(meuhedet_chunk)
            
            # Chunk 3: Clalit (כללית) services and coverage
            clalit_chunk = self._extract_hmo_chunk(clean_content, service_name, 'clalit', 'כללית')
            chunks.append(clalit_chunk)
            
            # Clean up
            del content, clean_content
            gc.collect()
            
            return chunks
            
        except Exception as e:
            logger.error(f"Error creating chunks for {html_file}: {e}")
            return []
    
    def _clean_html(self, html_content: str) -> str:
        """Clean HTML content"""
        # Remove scripts and styles
        html_content = re.sub(r'<script[^>]*>.*?</script>', '', html_content, flags=re.DOTALL)
        html_content = re.sub(r'<style[^>]*>.*?</style>', '', html_content, flags=re.DOTALL)
        
        # Remove HTML tags but keep text
        text_content = re.sub(r'<[^>]+>', ' ', html_content)
        
        # Clean whitespace
        text_content = re.sub(r'\s+', ' ', text_content).strip()
        
        return text_content
    

    def _extract_hmo_chunk(self, content: str, service_name: str, hmo_english: str, hmo_hebrew: str) -> Dict[str, Any]:
        """Extract HMO-specific chunk with all relevant information"""
        try:
            # Find all content related to this specific HMO
            hmo_content = self._find_hmo_specific_content(content, hmo_hebrew)
            
            # Also look for website and contact information
            website_info = self._extract_website_info(content, hmo_hebrew)
            contact_info = self._extract_contact_info(content, hmo_hebrew)
            
            # Combine all information
            full_content = hmo_content
            if website_info:
                full_content += f"\n\n{website_info}"
            if contact_info:
                full_content += f"\n\n{contact_info}"
            
            if not full_content.strip():
                # Fallback: create a chunk with basic info if HMO-specific content not found
                full_content = f"שירותי {service_name} עבור {hmo_hebrew} - מידע כללי על השירותים הזמינים."
            
            return {
                'content': full_content,
                'service': service_name,
                'chunk_type': hmo_english,
                'chunk_id': f"{service_name}_{hmo_english}",
                'hmo': hmo_english,
                'hmo_hebrew': hmo_hebrew,
                'description': f'{hmo_hebrew} services and coverage for {service_name}'
            }
            
        except Exception as e:
            logger.error(f"Error extracting {hmo_english} chunk: {e}")
            return {
                'content': f"מידע על {service_name} עבור {hmo_hebrew}",
                'service': service_name,
                'chunk_type': hmo_english,
                'chunk_id': f"{service_name}_{hmo_english}",
                'hmo': hmo_english,
                'hmo_hebrew': hmo_hebrew,
                'description': f'{hmo_hebrew} services for {service_name}'
            }
    
    def _find_hmo_specific_content(self, content: str, hmo_hebrew: str) -> str:
        """Find all content specific to a particular HMO"""
        try:
            # Split content into sections
            sections = content.split('\n')
            hmo_sections = []
            
            # Look for sections that contain the HMO name
            current_section = ""
            in_hmo_section = False
            
            for line in sections:
                # Check if this line contains the HMO name
                if hmo_hebrew in line:
                    in_hmo_section = True
                    current_section = line
                elif in_hmo_section:
                    # Continue collecting lines until we hit another HMO or major separator
                    if any(other_hmo in line for other_hmo in ['מכבי', 'מאוחדת', 'כללית']) and hmo_hebrew not in line:
                        # We hit another HMO, stop collecting
                        break
                    current_section += "\n" + line
            
            if current_section:
                # Clean up the collected content
                cleaned_content = re.sub(r'\s+', ' ', current_section).strip()
                return cleaned_content
            
            # If no specific section found, try to find HMO mentions in the entire content
            hmo_mentions = []
            for i, line in enumerate(sections):
                if hmo_hebrew in line:
                    # Get the line and a few lines before and after for context
                    start_idx = max(0, i - 2)
                    end_idx = min(len(sections), i + 3)
                    context_lines = sections[start_idx:end_idx]
                    hmo_mentions.extend(context_lines)
            
            if hmo_mentions:
                # Also look for website and contact sections that might be at the bottom
                website_sections = self._find_website_sections(content)
                if website_sections:
                    hmo_mentions.extend(website_sections)
                
                # Clean and combine all content
                all_content = "\n".join(hmo_mentions)
                cleaned_content = re.sub(r'\s+', ' ', all_content).strip()
                return cleaned_content
            
            return f"מידע כללי על שירותים עבור {hmo_hebrew}"
            
        except Exception as e:
            logger.error(f"Error finding HMO content for {hmo_hebrew}: {e}")
            return f"מידע על שירותים עבור {hmo_hebrew}"
    
    def _find_website_sections(self, content: str) -> List[str]:
        """Find website and contact information sections that are often at the bottom"""
        try:
            sections = content.split('\n')
            website_sections = []
            
            # Look for common website section headers
            website_keywords = ['אתר', 'website', 'Website', 'לפרטים נוספים', 'מידע נוסף', 'contact', 'Contact']
            
            for i, line in enumerate(sections):
                if any(keyword in line for keyword in website_keywords):
                    # Get this line and a few lines after for context
                    end_idx = min(len(sections), i + 5)
                    context_lines = sections[i:end_idx]
                    website_sections.extend(context_lines)
            
            return website_sections
            
        except Exception as e:
            logger.error(f"Error finding website sections: {e}")
            return []
    
    def _extract_website_info(self, content: str, hmo_hebrew: str) -> str:
        """Extract website information for a specific HMO"""
        try:
            # Look for website links in the content
            website_pattern = r'https?://[^\s<>"]+'
            websites = re.findall(website_pattern, content)
            
            # Filter websites that seem related to the HMO
            hmo_websites = []
            for website in websites:
                if any(hmo_keyword in website.lower() for hmo_keyword in ['maccabi', 'meuhedet', 'clalit', 'מכבי', 'מאוחדת', 'כללית']):
                    hmo_websites.append(website)
            
            if hmo_websites:
                return f"אתר אינטרנט: {', '.join(hmo_websites)}"
            
            return ""
            
        except Exception as e:
            logger.error(f"Error extracting website info for {hmo_hebrew}: {e}")
            return ""
    
    def _extract_contact_info(self, content: str, hmo_hebrew: str) -> str:
        """Extract contact information for a specific HMO"""
        try:
            # Look for phone numbers and contact details
            phone_pattern = r'(?:טלפון|phone|Phone):\s*([0-9\-\*]+)'
            phones = re.findall(phone_pattern, content, re.IGNORECASE)
            
            contact_info = []
            if phones:
                contact_info.append(f"טלפון: {', '.join(phones)}")
            
            # Look for extension information
            extension_pattern = r'שלוחה\s*(\d+)'
            extensions = re.findall(extension_pattern, content)
            if extensions:
                contact_info.append(f"שלוחה: {', '.join(extensions)}")
            
            if contact_info:
                return "פרטי קשר:\n" + "\n".join(contact_info)
            
            return ""
            
        except Exception as e:
            logger.error(f"Error extracting contact info for {hmo_hebrew}: {e}")
            return ""
    
    def _create_embeddings(self):
        """Create embeddings for all chunks"""
        try:
            if not self.azure_client:
                logger.warning("Azure client not available, using simple embeddings")
                self._create_simple_embeddings()
                return
            
            logger.info("Creating Azure OpenAI embeddings...")
            
            # Process in small batches
            batch_size = 6  # Process 6 chunks at a time
            total_batches = (len(self.chunks) + batch_size - 1) // batch_size
            
            for i in range(0, len(self.chunks), batch_size):
                batch_end = min(i + batch_size, len(self.chunks))
                batch_chunks = self.chunks[i:batch_end]
                
                logger.info(f"Processing batch {i//batch_size + 1}/{total_batches}")
                
                # Create embeddings for this batch
                batch_embeddings = []
                for chunk in batch_chunks:
                    try:
                        embedding = self._get_azure_embedding(chunk['content'])
                        batch_embeddings.append(embedding)
                    except Exception as e:
                        logger.warning(f"Azure embedding failed for {chunk['chunk_id']}: {e}")
                        # Use fallback
                        fallback_embedding = self._create_simple_embedding(chunk['content'])
                        batch_embeddings.append(fallback_embedding)
                
                # Add to main list
                self.embeddings.extend(batch_embeddings)
                
                # Clean up batch
                del batch_embeddings
                gc.collect()
                
                # Small delay
                time.sleep(0.1)
            
            logger.info(f"Successfully created {len(self.embeddings)} embeddings")
            
        except Exception as e:
            logger.error(f"Error creating embeddings: {e}")
            logger.info("Falling back to simple embeddings")
            self._create_simple_embeddings()
    
    def _get_azure_embedding(self, text: str) -> List[float]:
        """Get embedding from Azure OpenAI"""
        try:
            response = self.azure_client.embeddings.create(
                input=text,
                model="text-embedding-ada-002"
            )
            return response.data[0].embedding
        except Exception as e:
            logger.warning(f"Azure embedding failed: {e}")
            return self._create_simple_embedding(text)
    
    def _create_simple_embeddings(self):
        """Create simple hash-based embeddings"""
        logger.info("Creating simple embeddings...")
        
        for chunk in self.chunks:
            embedding = self._create_simple_embedding(chunk['content'])
            self.embeddings.append(embedding)
        
        logger.info(f"Created {len(self.embeddings)} simple embeddings")
    
    def _create_simple_embedding(self, text: str) -> List[float]:
        """Create simple hash-based embedding"""
        import hashlib
        
        hash_obj = hashlib.md5(text.encode())
        hash_hex = hash_obj.hexdigest()
        
        # Create 128-dimensional embedding
        embedding = []
        for i in range(0, len(hash_hex), 2):
            if len(embedding) >= 128:
                break
            hex_pair = hash_hex[i:i+2]
            embedding.append(float(int(hex_pair, 16)) / 255.0)
        
        while len(embedding) < 128:
            embedding.append(0.0)
        
        return embedding[:128]
    
    def _build_faiss_index(self):
        """Build FAISS index from embeddings"""
        try:
            if not self.embeddings:
                logger.warning("No embeddings available")
                return
            
            logger.info("Building FAISS index...")
            
            # Convert to numpy array
            embeddings_array = np.array(self.embeddings, dtype=np.float32)
            dimension = embeddings_array.shape[1]
            
            # Build index
            self.faiss_index = faiss.IndexFlatL2(dimension)
            self.faiss_index.add(embeddings_array)
            
            # Clear numpy array to save memory
            del embeddings_array
            gc.collect()
            
            logger.info(f"FAISS index built with {self.faiss_index.ntotal} vectors")
            
        except Exception as e:
            logger.error(f"Error building FAISS index: {e}")
            self.faiss_index = None
    
    def search_services(self, query: str, hmo_name: Optional[str] = None, 
                       insurance_tier: Optional[str] = None, top_k: int = 3, language: str = "he") -> str:
        """Search using vector similarity with HMO-specific filtering and keyword fallback"""
        try:
            if self.faiss_index and self.embeddings:
                # Enhance query for better cross-language search
                enhanced_query = self._enhance_query_for_multilingual_search(query, language)
                
                # Try vector search first with HMO filtering
                vector_results = self._vector_search(enhanced_query, top_k, language, hmo_name)
                
                # If vector search returns no results or very short results, try keyword search
                if "לא נמצא מידע" in vector_results or len(vector_results) < 100:
                    logger.info("Vector search returned limited results, trying keyword search")
                    keyword_results = self._keyword_search(enhanced_query, top_k, language, hmo_name)
                    if keyword_results and "לא נמצא מידע" not in keyword_results:
                        return keyword_results
                
                return vector_results
            else:
                logger.warning("Vector search not available")
                return "Vector search system not ready"
        except Exception as e:
            logger.error(f"Error in search: {e}")
            return "שגיאה בחיפוש המידע."
    
    def _enhance_query_for_multilingual_search(self, query: str, language: str) -> str:
        """Enhance query for better cross-language search performance"""
        try:
            # Common medical terms mapping (Hebrew <-> English)
            medical_terms_mapping = {
                # Dental services
                'dental': ['שיניים', 'שיני', 'דנטלי'],
                'teeth': ['שיניים', 'שיני'],
                'dentist': ['רופא שיניים', 'רופאת שיניים'],
                
                # Alternative medicine
                'reflexology': ['רפלקסולוגיה'],
                'acupuncture': ['דיקור סיני', 'אקופונקטורה'],
                'shiatsu': ['שיאצו'],
                'naturopathy': ['נטורופתיה'],
                'homeopathy': ['הומאופתיה'],
                'chiropractic': ['כירופרקטיקה'],
                
                # Medical services
                'medical': ['רפואי', 'רפואית'],
                'health': ['בריאות', 'בריאותי'],
                'service': ['שירות', 'שירותים'],
                'treatment': ['טיפול', 'טיפולים'],
                'therapy': ['תרפיה', 'טיפול'],
                
                # HMO terms
                'hmo': ['קופת חולים', 'קופה'],
                'insurance': ['ביטוח', 'ביטוחי'],
                'coverage': ['כיסוי', 'כיסוי ביטוחי'],
                'benefit': ['הטבה', 'הטבות'],
                
                # Contact information
                'phone': ['טלפון', 'טלפונית'],
                'contact': ['קשר', 'פרטי קשר'],
                'website': ['אתר', 'אתר אינטרנט'],
                'appointment': ['תור', 'קביעת תור'],
                
                # Common medical procedures
                'consultation': ['ייעוץ', 'התייעצות'],
                'examination': ['בדיקה', 'בדיקות'],
                'diagnosis': ['אבחון', 'אבחנה'],
                'prescription': ['מרשם', 'תרופה']
            }
            
            enhanced_query = query
            
            # If query is in English, add Hebrew equivalents for better matching
            if language == "en" or not any('\u0590' <= char <= '\u05FF' for char in query):
                query_lower = query.lower()
                added_terms = []
                
                for english_term, hebrew_terms in medical_terms_mapping.items():
                    if english_term in query_lower:
                        added_terms.extend(hebrew_terms)
                
                if added_terms:
                    enhanced_query = f"{query} {' '.join(added_terms)}"
                    logger.info(f"Enhanced English query with Hebrew terms: {enhanced_query}")
            
            # If query is in Hebrew, add English equivalents
            elif any('\u0590' <= char <= '\u05FF' for char in query):
                query_lower = query.lower()
                added_terms = []
                
                for english_term, hebrew_terms in medical_terms_mapping.items():
                    if any(hebrew_term in query_lower for hebrew_term in hebrew_terms):
                        added_terms.append(english_term)
                
                if added_terms:
                    enhanced_query = f"{query} {' '.join(added_terms)}"
                    logger.info(f"Enhanced Hebrew query with English terms: {enhanced_query}")
            
            return enhanced_query
            
        except Exception as e:
            logger.error(f"Error enhancing query: {e}")
            return query
    
    def _vector_search(self, query: str, top_k: int = 3, language: str = "he", hmo_name: Optional[str] = None) -> str:
        """Vector similarity search with HMO-specific filtering"""
        try:
            # Get query embedding
            if self.azure_client:
                query_embedding = self._get_azure_embedding(query)
            else:
                query_embedding = self._create_simple_embedding(query)
            
            query_vector = np.array([query_embedding], dtype=np.float32)
            
            # Search FAISS index with more results to allow for HMO filtering
            search_k = min(top_k * 3, len(self.chunks))  # Get more results for filtering
            distances, indices = self.faiss_index.search(query_vector, search_k)
            
            # Filter results by HMO if specified
            filtered_chunks = []
            for idx in indices[0]:
                if idx < len(self.chunks):
                    chunk = self.chunks[idx]
                    if hmo_name:
                        # Check if chunk matches the requested HMO
                        if (hmo_name.lower() in chunk.get('hmo', '').lower() or 
                            hmo_name.lower() in chunk.get('hmo_hebrew', '').lower() or
                            hmo_name.lower() in chunk.get('chunk_type', '').lower()):
                            filtered_chunks.append(chunk)
                    else:
                        # No HMO filter, include all chunks
                        filtered_chunks.append(chunk)
                    
                    # Stop when we have enough filtered results
                    if len(filtered_chunks) >= top_k:
                        break
            
            # Format results with better structure for AI understanding
            results = []
            for i, chunk in enumerate(filtered_chunks):
                result_text = f"SOURCE {i+1}: [{chunk['service']} - {chunk['chunk_type']}]\n{chunk['content']}"
                results.append(result_text)
            
            if results:
                # Add a header to make it clear this is retrieved information
                if language == "he":
                    header = "=== מידע שנאסף ממסד הנתונים ===\n"
                    no_results = "לא נמצא מידע רלוונטי לשאלה שלך במסד הנתונים."
                else:
                    header = "=== Information Retrieved from Database ===\n"
                    no_results = "No relevant information found in the database for your question."
                
                return header + "\n\n".join(results)
            else:
                return no_results
            
        except Exception as e:
            logger.error(f"Error in vector search: {e}")
            if language == "he":
                return "שגיאה בחיפוש המידע."
            else:
                return "Error searching for information."
    
    def _keyword_search(self, query: str, top_k: int = 3, language: str = "he", hmo_name: Optional[str] = None) -> str:
        """Fallback keyword search when vector search fails, with HMO filtering and cross-language support"""
        try:
            query_lower = query.lower()
            results = []
            
            # Extract key terms from query (both languages)
            query_terms = query_lower.split()
            
            # Add cross-language medical terms for better matching
            cross_language_terms = self._get_cross_language_terms(query_terms)
            all_search_terms = query_terms + cross_language_terms
            
            logger.info(f"Keyword search using terms: {all_search_terms}")
            
            # Search through all chunks for keyword matches
            for chunk in self.chunks:
                # Apply HMO filtering if specified
                if hmo_name:
                    if not (hmo_name.lower() in chunk.get('hmo', '').lower() or 
                           hmo_name.lower() in chunk.get('hmo_hebrew', '').lower() or
                           hmo_name.lower() in chunk.get('chunk_type', '').lower()):
                        continue  # Skip chunks that don't match the HMO
                
                chunk_content_lower = chunk['content'].lower()
                
                # Check if any search terms are in the chunk
                if any(term in chunk_content_lower for term in all_search_terms):
                    result_text = f"SOURCE: [{chunk['service']} - {chunk['chunk_type']}]\n{chunk['content']}"
                    results.append(result_text)
                    
                    if len(results) >= top_k:
                        break
            
            if results:
                if language == "he":
                    header = "=== מידע שנמצא בחיפוש מילות מפתח ===\n"
                else:
                    header = "=== Information Found via Keyword Search ===\n"
                return header + "\n\n".join(results)
            else:
                if language == "he":
                    return "לא נמצא מידע רלוונטי לשאלה שלך במסד הנתונים."
                else:
                    return "No relevant information found in the database for your question."
                    
        except Exception as e:
            logger.error(f"Error in keyword search: {e}")
            if language == "he":
                return "שגיאה בחיפוש המידע."
            else:
                return "Error searching for information."
    
    def _get_cross_language_terms(self, query_terms: List[str]) -> List[str]:
        """Get cross-language terms for better keyword matching"""
        try:
            # Medical terms mapping for cross-language search
            cross_language_mapping = {
                # Dental
                'dental': ['שיניים', 'שיני'],
                'teeth': ['שיניים', 'שיני'],
                'שיניים': ['dental', 'teeth'],
                'שיני': ['dental', 'teeth'],
                
                # Alternative medicine
                'reflexology': ['רפלקסולוגיה'],
                'רפלקסולוגיה': ['reflexology'],
                'acupuncture': ['דיקור', 'דיקור סיני'],
                'דיקור': ['acupuncture'],
                'דיקור סיני': ['acupuncture'],
                
                # Medical services
                'medical': ['רפואי', 'רפואית'],
                'רפואי': ['medical'],
                'רפואית': ['medical'],
                'health': ['בריאות', 'בריאותי'],
                'בריאות': ['health'],
                'בריאותי': ['health'],
                
                # HMO
                'hmo': ['קופה', 'קופת חולים'],
                'קופה': ['hmo'],
                'קופת חולים': ['hmo'],
                'insurance': ['ביטוח'],
                'ביטוח': ['insurance'],
                
                # Contact
                'phone': ['טלפון'],
                'טלפון': ['phone'],
                'website': ['אתר'],
                'אתר': ['website']
            }
            
            cross_terms = []
            for term in query_terms:
                if term in cross_language_mapping:
                    cross_terms.extend(cross_language_mapping[term])
            
            return cross_terms
            
        except Exception as e:
            logger.error(f"Error getting cross-language terms: {e}")
            return []
    
    def get_service_info(self, service_name: str, hmo_name: Optional[str] = None) -> str:
        """Get information about a specific service, optionally filtered by HMO"""
        service_chunks = [chunk for chunk in self.chunks if chunk['service'] == service_name]
        
        # Apply HMO filtering if specified
        if hmo_name:
            service_chunks = [chunk for chunk in service_chunks 
                            if (hmo_name.lower() in chunk.get('hmo', '').lower() or 
                                hmo_name.lower() in chunk.get('hmo_hebrew', '').lower() or
                                hmo_name.lower() in chunk.get('chunk_type', '').lower())]
        
        if service_chunks:
            # Sort by HMO for better organization
            hmo_order = {'maccabi': 1, 'meuhedet': 2, 'clalit': 3}
            service_chunks.sort(key=lambda x: hmo_order.get(x['chunk_type'], 999))
            
            formatted_content = []
            for chunk in service_chunks:
                hmo_display = chunk.get('hmo_hebrew', chunk.get('chunk_type', 'Unknown'))
                formatted_content.append(f"[{hmo_display}] {chunk['content']}")
            
            return "\n\n".join(formatted_content)
        
        if hmo_name:
            return f"לא נמצא מידע על {service_name} עבור {hmo_name}"
        return f"שירות {service_name} לא נמצא"
    
    def get_all_services(self) -> List[str]:
        """Get list of all available services"""
        return list(set(chunk['service'] for chunk in self.chunks))
    
    def get_service_count(self) -> int:
        """Get total number of services"""
        return len(self.get_all_services())
    
    def is_loaded(self) -> bool:
        """Check if knowledge base is loaded"""
        return len(self.chunks) > 0
    
    def get_stats(self) -> Dict[str, Any]:
        """Get knowledge base statistics"""
        chunk_types = {}
        hmo_counts = {}
        services = set()
        
        for chunk in self.chunks:
            chunk_type = chunk['chunk_type']
            chunk_types[chunk_type] = chunk_types.get(chunk_type, 0) + 1
            
            # Count HMOs
            hmo = chunk.get('hmo', chunk_type)
            hmo_counts[hmo] = hmo_counts.get(hmo, 0) + 1
            
            # Collect services
            services.add(chunk['service'])
        
        return {
            'total_chunks': len(self.chunks),
            'total_embeddings': len(self.embeddings),
            'has_faiss_index': self.faiss_index is not None,
            'embeddings_ready': self.is_embeddings_ready(),
            'chunk_types': chunk_types,
            'hmo_distribution': hmo_counts,
            'services': list(services),
            'total_services': len(services),
            'target_chunks': 18,
            'memory_efficient': True
        }
    
    def is_embeddings_ready(self) -> bool:
        """Check if embeddings are ready for vector search"""
        return (self.faiss_index is not None and 
                len(self.embeddings) == len(self.chunks) and 
                len(self.embeddings) > 0)
    
    def clear_embeddings(self):
        """Clear embeddings to free memory"""
        self.embeddings.clear()
        self.faiss_index = None
        gc.collect()
        logger.info("Embeddings cleared from memory")
    
    def __del__(self):
        """Cleanup when object is destroyed"""
        try:
            self.clear_embeddings()
            del self.chunks
            gc.collect()
        except:
            pass
