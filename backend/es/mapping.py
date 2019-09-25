INDEX = {
    "settings": {
        "number_of_shards": 1,
        "number_of_replicas": 1,
        # "index.refresh_interval": "3600s",
        "analysis": {
            "analyzer": {
                "my_ngram_analyzer": {
                    "tokenizer": "my_ngram_tokenizer",
                    "filter": [
                        "lowercase",
                        "asciifolding"
                    ]
                }
            },
            "tokenizer": {
                "my_ngram_tokenizer": {
                    "type": "edgeNGram",
                    "min_gram": "2",
                    "max_gram": "10",
                    "token_chars": ["letter", "digit"]
                }
            }
        }
    },
    "mappings": {
        "properties": {
            "id": {
                "type": "long",
                "coerce": False
            },
            "patient_id": {
                "type": "long"
            },
            "Patient's Name": {
                "type": "text",
                "fields": {
                    "lang_analyzed": {
                        "type": "text",
                        "analyzer": "my_ngram_analyzer"
                    }
                }
            },
            "SOP Class UID": {
                "type": "text",
                "fields": {
                    "lang_analyzed": {
                        "type": "text",
                        "analyzer": "my_ngram_analyzer"
                    }
                }
            },
            "Study Description": {
                "type": "text",
                "fields": {
                    "lang_analyzed": {
                        "type": "text",
                        "analyzer": "my_ngram_analyzer"
                    }
                }
            },
            "Series Description": {
                "type": "text",
                "fields": {
                    "lang_analyzed": {
                        "type": "text",
                        "analyzer": "my_ngram_analyzer"
                    }
                }
            },
            "Referring Physician's Name": {
                "type": "text",
                "fields": {
                    "lang_analyzed": {
                        "type": "text",
                        "analyzer": "my_ngram_analyzer"
                    }
                }
            },
            "Performing Physician's Name": {
                "type": "text",
                "fields": {
                    "lang_analyzed": {
                        "type": "text",
                        "analyzer": "my_ngram_analyzer"
                    }
                }
            },
        }
    }
}
