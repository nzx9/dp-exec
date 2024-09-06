from db.psql_connector import DB, default_config


def createCommunityModelTable():
    db = DB(default_config())
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS community_models (
            id VARCHAR(255) PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            description TEXT NOT NULL,
            version VARCHAR(10) NOT NULL,
            short_desc TEXT NOT NULL,
            long_desc TEXT NOT NULL,
            md_page TEXT NOT NULL,
            docs_link VARCHAR(512) NOT NULL,
            score FLOAT NOT NULL,
            hits JSON NOT NULL,
            rating FLOAT NOT NULL,
            model_path VARCHAR(512) DEFAULT NULL,
            model_type VARCHAR(512) DEFAULT NULL,
            encoder_path VARCHAR(512) DEFAULT NULL,
            encoder_type VARCHAR(512) DEFAULT NULL,
            dataset_name VARCHAR(255) DEFAULT NULL,
            dataset_url VARCHAR(512) DEFAULT NULL,
            dataset_sample json DEFAULT NULL,
            dataset_type VARCHAR(255) DEFAULT NULL,
            user_id VARCHAR(255) NOT NULL,
            free_to_use BOOLEAN DEFAULT FALSE NOT NULL,
            currecy VARCHAR(255) DEFAULT 'USD' NOT NULL,
            price_per_hit FLOAT DEFAULT 0.0 NOT NULL,
            linked_project VARCHAR(255) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id),
            FOREIGN KEY(linked_project) REFERENCES projects(id)
        )
    """
    )
    result = db.fetchone()
    return result


print(createCommunityModelTable())
