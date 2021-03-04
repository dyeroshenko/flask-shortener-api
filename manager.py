from url_services import UrlServices
from hashing import Hashing
from database import Database

class Manager:
    def __init__(self):
        self.url_services = UrlServices()
        self.hashing = Hashing()
        self.database = Database('url.db')

    def verify_url_and_add_to_db(self, url):
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
                    'short_id': id,
                    'url_domain': domain,
                    'full_url': full_url,
                    'visits': visits,
                    }
        
        else: 
            return {'status': 'Not OK! Invalid or duplicate URL'}

    def check_last_id_and_generate_new(self):
        with self.database as cursor:
            _SQL = 'SELECT MAX(id) FROM urls'
            cursor.execute(_SQL)
            last_id = cursor.fetchall()[0][0]

        return last_id + 1

    
    def get_and_decode_shortened_url(self, hashed_id):
        unhashed_id = self.hashing.decode_hash_key(hashed_id)

        try: 
            with self.database as cursor:
                # cursor.execute('SELECT visits FROM url WHERE id = ?', (unhashed_id[0],))
                # visits = int(cursor.fetchone()) + 1 
                # cursor.execute('UPDATE urls SET visits = ? WHERE id ?', (visits, unhashed_id[0]))
                cursor.execute('SELECT hashed_id, timestamp_CET, full_url, domain, visits FROM urls WHERE id = ?', (unhashed_id[0],))

                result = cursor.fetchone()
        
            return {
                    'hashed_id': result[0],
                    'timestamp_added_cet': result[1],
                    'full_url': result[2],
                    'domain': result[3],
                    'visits': result[4],
                    }
        except: 
            return {'status': 'Not OK! Invalid ID'}

    def show_all_urls(self):
        with self.database as cursor:
            cursor.execute('SELECT * FROM urls ORDER BY id ASC')
            fetch = cursor.fetchall()
        
        result = list()

        for record in fetch:
            result.append({'id': record[0], 
                        'hashed_id': record[1], 
                        'timestamp_added_cet': record[2], 
                        'full_url': record[3],
                        'domain': record[4],
                        'visits': record[5]})

        return result