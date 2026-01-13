class DataRegistry:
    def __init__(self):
        self.objects = {}
        self._subset_count = 0
        self._df_count = 0

    def put(self, obj):
        obj_id = self._next_id_for(obj)
        self.objects[obj_id] = obj
        return obj_id

    def get(self, obj_id):
        return self.objects[obj_id]

    def _next_id_for(self, obj):
        try:
            import pandas as pd
            import gwaslab as gl
        except Exception:
            pd = None
            gl = None
        if gl is not None and isinstance(obj, gl.Sumstats):
            obj_id = f"subset_{self._subset_count}"
            self._subset_count += 1
            return obj_id
        if pd is not None and isinstance(obj, pd.DataFrame):
            obj_id = f"df_{self._df_count}"
            self._df_count += 1
            return obj_id
        # Fallback generic id
        gen_id = f"obj_{len(self.objects)}"
        return gen_id

    def next_key(self):
        # Predict the next subset id (for filter operations)
        return f"subset_{self._subset_count}"
        
    def copy(self):
        return self.objects.copy()
    
    def _get_keys_list(self):
        """Get a list of keys in insertion order."""
        return list(self.objects.keys())
    
    def __len__(self):
        """Return the number of objects in the registry."""
        return len(self.objects)
    
    def __getitem__(self, key):
        """
        Support both string key access and integer index access.
        
        Examples:
            RESULTS["df_0"]  # String key access
            RESULTS[0]      # Integer index access (returns first object)
            RESULTS[0:2]    # Slice access (returns list of objects)
        """
        # Handle string keys directly
        if isinstance(key, str):
            if key in self.objects:
                return self.objects[key]
            raise KeyError(f"Key '{key}' not found in RESULTS")
        
        # Handle integer indices
        if isinstance(key, int):
            keys = self._get_keys_list()
            if key < 0:
                # Support negative indices
                key = len(keys) + key
            if 0 <= key < len(keys):
                return self.objects[keys[key]]
            raise IndexError(f"Index {key} out of range for RESULTS (length: {len(keys)})")
        
        # Handle slices
        if isinstance(key, slice):
            keys = self._get_keys_list()
            sliced_keys = keys[key]
            # Return a list of objects for the slice
            return [self.objects[k] for k in sliced_keys]
        
        raise TypeError(f"RESULTS indices must be strings, integers, or slices, not {type(key).__name__}")
    
    def __setitem__(self, key, value):
        """
        Support assignment like RESULTS["df_0"] = df or RESULTS[0] = df.
        
        Examples:
            RESULTS["df_0"] = df  # Direct assignment with string key
            RESULTS[0] = df       # Assignment by index (updates existing key)
        """
        # Handle string keys directly
        if isinstance(key, str):
            self.objects[key] = value
            return
        
        # Handle integer indices - update the object at that position
        if isinstance(key, int):
            keys = self._get_keys_list()
            if key < 0:
                # Support negative indices
                key = len(keys) + key
            if 0 <= key < len(keys):
                self.objects[keys[key]] = value
                return
            raise IndexError(f"Index {key} out of range for RESULTS (length: {len(keys)})")
        
        raise TypeError(f"RESULTS assignment keys must be strings or integers, not {type(key).__name__}")
    
    def __contains__(self, key):
        """Support 'in' operator: 'df_0' in RESULTS"""
        if isinstance(key, str):
            return key in self.objects
        if isinstance(key, int):
            keys = self._get_keys_list()
            if key < 0:
                key = len(keys) + key
            return 0 <= key < len(keys)
        return False
    
    def keys(self):
        """Return a view of all keys."""
        return self.objects.keys()
    
    def values(self):
        """Return a view of all values."""
        return self.objects.values()
    
    def items(self):
        """Return a view of all (key, value) pairs."""
        return self.objects.items()