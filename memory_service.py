from neo4j import GraphDatabase

class MemoryService:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
    
    def close(self):
        self.driver.close()
    
    def update_user_preferences(self, user_id, preferences):
        with self.driver.session() as session:
            session.run(
                """
                MERGE (u:User {id: $user_id})
                SET u.preferences = $preferences
                """,
                user_id=user_id, preferences=preferences
            )
    
    def get_user_preferences(self, user_id):
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (u:User {id: $user_id})
                RETURN u.preferences AS preferences
                """,
                user_id=user_id
            )
            record = result.single()
            return record["preferences"] if record else {}
