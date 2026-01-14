import json
import uuid
import os
import leanvec
import atexit
import gc
import time
import threading
import copy
from typing import List, Dict, Any, Optional

class LeanVecDB:
    def __init__(self, base_path: str = 'leanvec_root', auto_persist: bool = True):
        self.base_path = base_path
        if not os.path.exists(base_path):
            os.makedirs(base_path)

        self.collections: Dict[str, leanvec.LeanDB] = {}
        self.dimensions: Dict[str, int] = {}
        self._load_existing_collections()

        self.start_time = time.time()
        self.last_access_time = time.time()
        self.maintenance_interval = 86400 
        self.idle_threshold = 3600
        self.stop_maintenance = False
        
        self.m_thread = threading.Thread(target=self._maintenance_loop, daemon=True)
        self.m_thread.start()

        if auto_persist:
            atexit.register(self.persist_all)

    def _get_col_path(self, name: str) -> str:
        return os.path.join(self.base_path, name)

    def _load_existing_collections(self):
        if not os.path.exists(self.base_path):
            return
        for name in os.listdir(self.base_path):
            path = self._get_col_path(name)
            if os.path.isdir(path):
                cfg_path = os.path.join(path, 'config.json')
                if os.path.exists(cfg_path):
                    try:
                        with open(cfg_path, 'r') as f:
                            self.dimensions[name] = json.load(f).get('dimension')
                    except: pass

    def _ensure_collection(self, name: str) -> leanvec.LeanDB:
        self.last_access_time = time.time()
        if name not in self.collections:
            path = self._get_col_path(name)
            if not os.path.exists(path):
                os.makedirs(path)
            self.collections[name] = leanvec.LeanDB(path)
        return self.collections[name]

    def list_collections(self) -> List[str]:
        return list(set(list(self.collections.keys()) + list(self.dimensions.keys())))

    def store_embedding(self, embedding: List[float], metadata_dict: Optional[Dict[str, Any]] = None, collection: str = "default", ttl: Optional[int] = None) -> str:
        """Store a single embedding with optional TTL (in seconds)."""
        metadatas = [metadata_dict] if metadata_dict is not None else None
        return self.store_embeddings_batch([embedding], metadatas, collection=collection, ttl=ttl)[0]

    def store_embeddings_batch(self, embeddings: List[List[float]], metadatas: Optional[List[Dict[str, Any]]] = None, collection: str = "default", ttl: Optional[int] = None) -> List[str]:
        if not embeddings: return []
        
        db = self._ensure_collection(collection)
        input_dim = len(embeddings[0])
        
        # Dimension validation and persistence
        if collection not in self.dimensions:
            self.dimensions[collection] = input_dim
            with open(os.path.join(self._get_col_path(collection), 'config.json'), 'w') as f:
                json.dump({'dimension': input_dim}, f)
        elif input_dim != self.dimensions[collection]:
            raise ValueError(f"Dimension Mismatch: Expected {self.dimensions[collection]}, Got {input_dim}")

        if metadatas is None: 
            metadatas = [{} for _ in range(len(embeddings))]
        
        ids = []
        for vec, meta_orig in zip(embeddings, metadatas):
            # Crucial: copy metadata to avoid shared reference bugs in batch lists
            meta = copy.deepcopy(meta_orig)
            
            # ID generation logic (supports explicit 'id' or '_id')
            doc_id = str(meta.get("id") or meta.get("_id") or uuid.uuid4())
            meta["id"] = doc_id
            ids.append(doc_id)
            
            # Add to DB including the TTL parameter
            db.add(doc_id, vec, json.dumps(meta), ttl)
            
        return ids

    def search(self, query_embedding: List[float], k: int = 5, filters: Optional[Dict[str, Any]] = None, collection: str = "default", autocut: bool = False) -> List[Dict[str, Any]]:
        db = self._ensure_collection(collection)
        filter_str = json.dumps(filters) if filters else None
        raw_results = db.search(query_embedding, k, filter_str)
        
        results = [{"id": d, "score": s} for d, s in raw_results]
        if autocut and len(results) > 1:
            scores = [r["score"] for r in results]
            cut_idx = self._calculate_autocut(scores)
            if cut_idx: results = results[:cut_idx]
        return results

    def _calculate_autocut(self, scores: List[float]) -> Optional[int]:
        for i in range(1, len(scores)):
            if scores[i-1] > 0 and (scores[i] - scores[i-1]) / scores[i-1] > 0.2:
                return i
        return None

    def delete(self, metadata_filter: Dict[str, Any], collection: str = "default") -> int:
        if collection not in self.collections and collection not in self.dimensions:
            return 0
        db = self._ensure_collection(collection)
        return db.delete_by_filter(json.dumps(metadata_filter))

    def count(self, collection: str = "default") -> int:
        if collection not in self.collections and collection not in self.dimensions:
            return 0
        return self._ensure_collection(collection).count()

    def persist_all(self):
        # Check if base path still exists to avoid OS Error 2 during cleanup
        if not os.path.exists(self.base_path):
            return
            
        for name, db in list(self.collections.items()):
            try:
                gc.collect()
                db.persist()
            except Exception:
                pass

    def persist(self, collection: str = "default"):
        """Persist a specific collection."""
        if collection in self.collections:
            self.collections[collection].persist()

    def _maintenance_loop(self):
        while not self.stop_maintenance:
            time.sleep(1)
            uptime = time.time() - self.start_time
            idle_time = time.time() - self.last_access_time
            if uptime > self.maintenance_interval and idle_time > self.idle_threshold:
                self.persist_all()
                self.start_time = time.time()

    def vacuum(self, collection: str = "default"):
        """Stop-the-world compaction for a specific collection."""
        db = self._ensure_collection(collection)
        db.vacuum()
