from typing import Dict, List, Tuple

from url_services import UrlServices
from hashing import Hashing
from database import Database

class Manager:
    def __init__(self):
        self.url_services = UrlServices()
        self.hashing = Hashing()
        self.database = Database('url.db')

    def verify_url_and_add_to_db(self, url: str) -> Dict[str, str]:
        if (self.url_services.check_is_valid_url(url) 
            and not self.url_services.check_if_duplicate(url)):

            timestamp = self.url_services.timestamp
            id = self.check_last_id_and_generate_new()
            short_id = self.hashing.generate_hash_key(id)
            domain = self.url_services.get_domain(url)
            full_url = url
            visits = 0

            with self.database as cursor:
                _SQL = 'INSERT INTO urls (id, hashed_id, timestamp_CET, full_url, domain, visits) VALUES (?, ?, ?, ?, ?, ?)'
                cursor.execute(_SQL, (
                                        id, 
                                        short_id,
                                        timestamp,
                                        full_url,
                                        domain,
                                        visits
                                    ))

            return {
                    'status': 'OK! Url added',
                    'timestamp_added': timestamp, 
                    'short_id': short_id,
                    'url_domain': domain,
                    'full_url': full_url,
                    }
        
        else: 
            return {'status': 'Not OK! Invalid or duplicate URL'}

    
    def get_shortened_url(self, key: str) -> Dict[int, str]:
        unhashed_key = self.decode_shortened_key(key)

        try: 
            with self.database as cursor:
                cursor.execute('SELECT hashed_id, timestamp_CET, full_url, domain, visits FROM urls WHERE id = ?', (unhashed_key,))
                result = cursor.fetchone()
        
            return {
                    'short_id': result[0],
                    'timestamp_added_cet': result[1],
                    'full_url': result[2],
                    'domain': result[3],
                    'visits': result[4],
                    }
        except: 
            return {'status': 'Not OK! Invalid ID'}


    def show_all_urls(self) -> List[Dict[str, str]]:
        raw_resut = self.get_full_data_from_db()
        result = list()

        for record in raw_resut:
            result.append({
                            'short_id': record[1], 
                            'timestamp_added_cet': record[2], 
                            'domain': record[3],
                            'full_url': record[4],
                            'visits': record[5]
                        })

        return result

    def get_full_url_for_redirect(self, key: str) -> str:
        key = self.decode_shortened_key(key)
        self.increment_visit_count_for_url(key)
        
        with self.database as cursor:
            cursor.execute('SELECT full_url FROM urls WHERE id = ?', (key,))
            result = cursor.fetchone()

        return result[0]

    def get_full_data_from_db(self) -> List[Tuple[int, str]]:
        with self.database as cursor:
            cursor.execute('SELECT id, hashed_id, timestamp_CET, domain, full_url, visits FROM urls ORDER BY id ASC')
            result = cursor.fetchall()

            return result

    def check_last_id_and_generate_new(self) -> int:
        with self.database as cursor:
            _SQL = 'SELECT MAX(id) FROM urls'
            cursor.execute(_SQL)
            last_id = cursor.fetchall()[0][0]

        return last_id + 1

    def decode_shortened_key(self, key: str) -> int:
        id = self.hashing.decode_hash_key(key)

        return id[0]

    def increment_visit_count_for_url(self, key: int) -> None:
        with self.database as cursor:
            cursor.execute('SELECT visits FROM urls WHERE id = ?', (key,))
            visits = int(cursor.fetchone()[0]) + 1 
            cursor.execute('UPDATE urls SET visits = ? WHERE id = ?', (visits, key))