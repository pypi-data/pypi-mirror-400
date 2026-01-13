import numpy as np
import pandas as pd
import time
from typing import List, Optional, Tuple, Dict, Any, Union
from sklearn.decomposition import FastICA
from sklearn.utils import check_array
from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.preprocessing import LabelEncoder
from scipy.optimize import differential_evolution
import pyswarms as ps
import warnings


warnings.filterwarnings('ignore')

# --- Helper Classes ---

class ReconstructionICA(FastICA):
    """ICA with reconstruction functionality."""
    
    def __init__(self, n_components=None, random_state=None):
        super().__init__(
            n_components=n_components,
            algorithm='parallel',
            whiten='unit-variance',
            fun='logcosh',
            max_iter=1000,
            tol=1e-5,
            random_state=random_state
        )
        self.mixing_ = None
        self.mean_ = None

    def fit(self, X, y=None):
        """Fit the model and compute the mixing matrix."""
        X = check_array(X, copy=True, dtype=np.float64)
        # Store the mean of the unwhitened data
        self.mean_ = np.mean(X, axis=0) if self.whiten in (True, 'unit-variance', 'arbitrary-variance') else np.zeros(X.shape[1])
        super().fit(X)
        
        # Calculate A (Mixing Matrix) for explicit reconstruction: X = S @ A + mean
        self.mixing_ = np.linalg.pinv(self.components_)
        
        print(f"ICA fitted with {self.n_components} components.")
        return self

    def reconstruct(self, S):
        """Reconstruct data from independent components."""
        S = check_array(S, dtype=np.float64)
        if self.mixing_ is None:
            raise ValueError("Model must be fitted before reconstruction.")
        if S.ndim == 1:
            S = S.reshape(1, -1)
            
        X_reconstructed = np.dot(S, self.mixing_.T) + self.mean_
        
        return X_reconstructed

class DataPreprocessor:
    """Internal general preprocessor for feature and target encoding."""
    
    def __init__(self, random_state=None):
        self.random_state = random_state
        self.label_encoders = {}
        self.feature_names = None
        self.numerical_cols = None
        self.categorical_cols = None
        self.target_encoder = None
    
    def fit_transform(self, data: pd.DataFrame, target_column: str, drop_columns: List[str]) -> Tuple[np.ndarray, np.ndarray, List[str]]:
        """Fit and transform the dataset."""
        data = data.copy()
        
        # Drop specified columns
        drop_cols = [col for col in drop_columns if col in data.columns]
        data = data.drop(drop_cols, axis=1)
        
        # Split target
        y_series = data[target_column]
        data = data.drop(target_column, axis=1)

        # Identify numerical and categorical columns
        self.numerical_cols = data.select_dtypes(include=[np.number]).columns.tolist()
        self.categorical_cols = data.select_dtypes(include=['object', 'category']).columns.tolist()
        
        # Handle missing values and convert to float/string
        for col in self.numerical_cols:
            data[col] = pd.to_numeric(data[col], errors='coerce')
            data[col].fillna(data[col].median(), inplace=True)
        
        for col in self.categorical_cols:
            data[col] = data[col].astype(str)
            data[col].fillna(data[col].mode()[0], inplace=True)
        
        # Encode categorical features
        for col in self.categorical_cols:
            le = LabelEncoder()
            data[col] = le.fit_transform(data[col])
            self.label_encoders[col] = le
        
        # Encode target
        self.target_encoder = LabelEncoder()
        y = self.target_encoder.fit_transform(y_series)
        if len(self.target_encoder.classes_) != 2:
            raise ValueError("RICExplainer requires binary classification (two classes only).")
        
        self.feature_names = data.columns.tolist()
        X = data.values.astype(np.float64)
        return X, y, self.feature_names
    
    def inverse_transform_features(self, X: np.ndarray) -> pd.DataFrame:
        """Convert numerical features back to DataFrame with feature names."""
        return pd.DataFrame(X, columns=self.feature_names)

# --- Main Explainer Class ---

class RICExplainer:
    """
    Ranked Independent Components (RIC) Explainer for Counterfactual Generation.
    """
    
    DEFAULT_CONFIG = {
        'N_COMPONENTS': None,
        'MASKED': [],
        'TYPE_MODE': 'automatic',
        'MANUAL_DISCRETE_FEATURES': [],
        'BOUNDS_MODE': 'automatic',
        'MANUAL_BOUNDS': {},
        'GLOBAL_OPTIMIZER': 'pso',
        'MAX_ITER': 10,
        'POP_SIZE': 10,
        'W': 0.729,
        'C1': 1.49445,
        'C2': 1.49445,
        'TARGET_THRESHOLD': 0.5,
        'BOUNDS_RANGE': 2.0,
        'TOP_K': 1,
        'STEP_NUM': 100,
        'RANDOM_STATE': 42,
        'MAX_DIST': 1e18 
    }
    
    def __init__(self, config: Optional[Dict[str, Any]] = None, classifier: Optional[Any] = None):
        """
        Initializes the RICExplainer.

        Args:
            config: A dictionary with configuration settings. If None, uses default settings.
            classifier: A scikit-learn compatible classifier object (e.g., RandomForestClassifier, 
                        GradientBoostingClassifier). If None, a RandomForestClassifier is used as default.
        """
        self.config = self._load_config(config)
        self.random_state = self.config['RANDOM_STATE']
        
        self.preprocessor = DataPreprocessor(random_state=self.random_state)
        
        # Use provided classifier or default to RandomForestClassifier
        if classifier is not None:
            self.classifier = classifier
        else:
            self.classifier = RandomForestClassifier(random_state=self.random_state)
            
        self.ica = ReconstructionICA(n_components=self.config['N_COMPONENTS'], random_state=self.random_state)
        
        # Attributes set during fit
        self.feature_names: List[str] = []
        self.baseline: Optional[np.ndarray] = None
        self.importances_: Optional[np.ndarray] = None
        self.selected_components_: Optional[np.ndarray] = None
        self.S_train: Optional[np.ndarray] = None
        self.target_classes: Optional[np.ndarray] = None
        self.unmasked_indices: List[int] = []
        self.masked_indices: List[int] = []
        self.feature_bounds: Dict[str, Tuple[float, float]] = {}
        self.discrete_features: List[str] = []
        self.continuous_features: List[str] = []
        self._fitted = False
    
    def _load_config(self, config_input: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Loads and merges configuration from a dictionary."""
        final_config = self.DEFAULT_CONFIG.copy()
        
        if isinstance(config_input, dict):
            final_config.update(config_input)
            
        return final_config

    def fit(self, X: Union[pd.DataFrame, np.ndarray], y: Union[pd.Series, np.ndarray], target_column: Optional[str] = None) -> 'RICExplainer':
        """
        Fits the data preprocessor, ICA model, and the classifier.
        """
        if isinstance(X, np.ndarray):
            if target_column is None: target_column = 'target_dummy_name'
            X_df = pd.DataFrame(X, columns=[f'feature_{i}' for i in range(X.shape[1])])
            X_df[target_column] = y
        elif isinstance(X, pd.DataFrame):
            if target_column is None: raise ValueError("If X is a DataFrame, 'target_column' must be provided.")
            X_df = X.copy()
            if y is not None and target_column not in X_df.columns:
                X_df[target_column] = y
        else:
            raise TypeError("X must be a pandas DataFrame or a numpy array.")
            
        if target_column is None or target_column not in X_df.columns:
             raise ValueError("The target column could not be identified/included in the data for preprocessing.")
            
        # 1. Preprocessing
        X_np, y_np, self.feature_names = self.preprocessor.fit_transform(
            X_df, 
            target_column=target_column, 
            drop_columns=self.config.get('DROP_COLUMNS', [])
        )
        self.target_classes = self.preprocessor.target_encoder.classes_
        
        # 2. Feature separation (masked vs. unmasked)
        feature_indices = {name: i for i, name in enumerate(self.feature_names)}
        self.unmasked_indices = [idx for name, idx in feature_indices.items() if name not in self.config['MASKED']]
        self.masked_indices = [idx for name, idx in feature_indices.items() if name in self.config['MASKED']]
        
        X_unmasked = X_np[:, self.unmasked_indices]
        X_masked = X_np[:, self.masked_indices]
        
        # 3. ICA Fitting on unmasked data
        if X_unmasked.shape[1] > 0:
            self.ica.fit(X_unmasked)
            self.S_train = self.ica.transform(X_unmasked)
            if self.config['N_COMPONENTS'] is None:
                self.config['N_COMPONENTS'] = self.S_train.shape[1]
        else:
            self.config['N_COMPONENTS'] = 0
            self.S_train = np.empty((X_np.shape[0], 0))
            print("Warning: All features are masked or no numerical features found. ICA is skipped.")

        # 4. Classifier Fitting (on independent components + masked features)
        X_train_combined = np.hstack((self.S_train, X_masked))
        self.classifier.fit(X_train_combined, y_np)
        
        # Calculate the baseline for the ICA component space
        self.baseline = np.mean(self.S_train, axis=0) if self.S_train.shape[0] > 0 else np.array([])
        
        # 5. Feature Type and Bounds Setup
        self._setup_feature_properties(X_np)
        
        # 6. Compute and Select Components
        self._compute_and_select_components(X_np)
        
        self._fitted = True
        return self

    def _setup_feature_properties(self, X_np: np.ndarray):
        """Internal helper to set up feature types (discrete/continuous) and bounds."""
        
        # --- Feature Type Enforcement ---
        self.discrete_features = []
        if self.config['TYPE_MODE'] == 'manual':
            self.discrete_features = self.config['MANUAL_DISCRETE_FEATURES']
        else:
            # Automatic detection
            for i, name in enumerate(self.feature_names):
                if name not in self.preprocessor.categorical_cols:
                    unique_values = np.unique(X_np[:, i])
                    if all(np.isclose(v, int(v)) for v in unique_values):
                        self.discrete_features.append(name)
        
        # Categorical features are always treated as discrete after label encoding
        self.discrete_features.extend(self.preprocessor.categorical_cols)
        self.discrete_features = list(set(self.discrete_features))
        
        self.continuous_features = [f for f in self.feature_names if f not in self.discrete_features]
        
        # --- Feature Bounds ---
        self.feature_bounds = {}
        if self.config['BOUNDS_MODE'] == 'manual':
            self.feature_bounds = self.config['MANUAL_BOUNDS']
        else:
            df_train = pd.DataFrame(X_np, columns=self.feature_names)
            for col in self.feature_names:
                self.feature_bounds[col] = (df_train[col].min(), df_train[col].max())

    def _compute_and_select_components(self, X_train: np.ndarray):
        """Internal helper to compute ICA importances and select the top-k/thresholded components."""
        if self.S_train is None or self.S_train.shape[1] == 0:
             self.importances_ = np.array([])
             self.selected_components_ = np.array([])
             return
        importances = []
        masked_feature_names = [self.feature_names[i] for i in self.masked_indices]
        
        if not masked_feature_names:
            masked_baseline = pd.Series(dtype='float64')
        else:
            df_train_features = pd.DataFrame(X_train, columns=self.feature_names)
            masked_baseline = df_train_features[masked_feature_names].mean(axis=0)

        class_index = 0 # Use the first target class for importance calculation
        
        for i in range(self.config['N_COMPONENTS']):
            min_val = np.min(self.S_train[:, i])
            max_val = np.max(self.S_train[:, i])
            if min_val == max_val:
                importances.append(0.0)
                continue
            
            points = np.linspace(min_val, max_val, self.config['STEP_NUM'] + 1)
            probas = []
            
            for val in points:
                s_synth = self.baseline.copy()
                s_synth[i] = val
                
                masked_part = masked_baseline.values.reshape(1, -1) if not masked_baseline.empty else np.empty((1, 0))
                combined_synth = np.hstack((s_synth.reshape(1, -1), masked_part))
                
                proba = self.classifier.predict_proba(combined_synth)[0, class_index]
                probas.append(proba)
            
            probas = np.array(probas)
            ders = np.diff(probas) / np.diff(points)
            importance = np.sum(np.abs(ders))
            importances.append(importance)
            
        self.importances_ = np.array(importances)
        
        abs_imp = np.abs(self.importances_)
        top_k = self.config['TOP_K']
        
        if top_k is not None and self.config['N_COMPONENTS'] > 0:
            ranks = np.argsort(abs_imp)[::-1]
            self.selected_components_ = ranks[:min(top_k, self.config['N_COMPONENTS'])]
        else:
            self.selected_components_ = np.arange(self.config['N_COMPONENTS']) 
        
        print(f"ICA: {self.config['N_COMPONENTS']} components found. {len(self.selected_components_)} components selected for CF generation.")


    def _run_optimization(self, instance: np.ndarray, S_instance: np.ndarray, instance_masked: np.ndarray,
                          target_class_idx: int, max_dist: float, found_cf_components: List[np.ndarray], diversity_radius: float) -> Optional[Tuple[np.ndarray, np.ndarray]]:
        """
        Core optimization logic for a single counterfactual.
        
        Hard penalty for constraints is fixed at 1e20.
        """
        n_selected = len(self.selected_components_)
        if n_selected == 0: return None, None

        target_threshold = self.config['TARGET_THRESHOLD']
        bounds_range = self.config['BOUNDS_RANGE']
        
        # Hardcoded penalty value as requested
        PENALTY = 1e20 
        
        def _single_cost(delta_selected):
            delta_full = np.zeros(self.config['N_COMPONENTS'])
            delta_full[self.selected_components_] = delta_selected
            s_cf = S_instance + delta_full
            
            # 1. Diversity Constraint
            if len(found_cf_components) > 0:
                for existing_delta in found_cf_components:
                    if np.linalg.norm(delta_selected - existing_delta) < diversity_radius:
                        return PENALTY 

            # 2. Reconstruction and Feature Enforcement
            X_cf_unmasked = self.ica.reconstruct(s_cf.reshape(1, -1))[0]
            X_cf = np.zeros_like(instance)
            X_cf[self.unmasked_indices] = X_cf_unmasked
            X_cf[self.masked_indices] = instance_masked
            
            # Apply Type and Bounds Enforcement
            for feat_idx, feat_name in enumerate(self.feature_names):
                min_val, max_val = self.feature_bounds.get(feat_name, (None, None))
                
                if feat_name in self.discrete_features:
                    X_cf[feat_idx] = round(X_cf[feat_idx])
                
                if min_val is not None and max_val is not None:
                    cf_val = X_cf[feat_idx]
                    if not (min_val - 1e-6 <= cf_val <= max_val + 1e-6):
                        return PENALTY

            # 3. Prediction Constraint
            X_cf_unmasked = X_cf[self.unmasked_indices]
            S_cf_constrained = self.ica.transform(X_cf_unmasked.reshape(1, -1))[0]
            
            masked_part = X_cf[self.masked_indices].reshape(1, -1) if X_cf[self.masked_indices].size > 0 else np.empty((1, 0))
            combined_cf = np.hstack((S_cf_constrained.reshape(1, -1), masked_part))
            
            proba = self.classifier.predict_proba(combined_cf)[0, target_class_idx] 
            
            # Target probability violation also uses the hard penalty
            if proba < target_threshold:
                return PENALTY

            # 4. Optimization Objective: L2 distance in feature space (unmasked part only)
            distance = np.linalg.norm(X_cf[self.unmasked_indices] - instance[self.unmasked_indices]) ** 2
            
            return distance
        
        def batched_cost(X_deltas):
            return np.array([_single_cost(delta) for delta in X_deltas])


        # --- Optimization Selection ---
        optimizer_mode = self.config['GLOBAL_OPTIMIZER'].lower()
        bounds = [(-bounds_range, bounds_range)] * n_selected
        
        gbest_x = None
        gbest_fun = 1e21 # Safely larger than PENALTY=1e20
        
        if optimizer_mode == 'de':
            res = differential_evolution(
                _single_cost, bounds, seed=self.random_state,
                maxiter=self.config['MAX_ITER'], popsize=self.config['POP_SIZE'],
                disp=False
            )
            gbest_x = res.x
            gbest_fun = res.fun
        
        elif optimizer_mode == 'pso':
            min_bound = np.array([b[0] for b in bounds])
            max_bound = np.array([b[1] for b in bounds])
            pso_bounds = (min_bound, max_bound)

            options = {'c1': self.config['C1'], 'c2': self.config['C2'], 'w': self.config['W']}
            optimizer = ps.single.GlobalBestPSO(
                n_particles=self.config['POP_SIZE'], dimensions=n_selected, 
                options=options, bounds=pso_bounds
            )
            
            gbest_fun, gbest_pos = optimizer.optimize(batched_cost, iters=self.config['MAX_ITER'], verbose=False)
            gbest_x = gbest_pos
        
        else:
            raise ValueError(f"Unknown global optimizer: {self.config['GLOBAL_OPTIMIZER']}. Use 'de' or 'pso'.")
        # --- End Optimization Selection ---
        
        # Check if a non-penalty solution was found, and if that solution is within the max_dist threshold
        if gbest_fun < max_dist and gbest_fun < PENALTY:
            # Final reconstruction and type enforcement
            delta_selected = gbest_x
            delta_full = np.zeros(self.config['N_COMPONENTS'])
            delta_full[self.selected_components_] = delta_selected
            S_cf = S_instance + delta_full
            
            X_cf_unmasked = self.ica.reconstruct(S_cf.reshape(1, -1))[0]
            X_cf = np.zeros_like(instance)
            X_cf[self.unmasked_indices] = X_cf_unmasked
            X_cf[self.masked_indices] = instance_masked

            for feat_name in self.discrete_features:
                feat_idx = self.feature_names.index(feat_name)
                X_cf[feat_idx] = round(X_cf[feat_idx])
                
            return X_cf, delta_selected
        
        return None, None

    def explain(self, X_input: Union[pd.DataFrame, np.ndarray], 
                num_cf: int = 1, 
                diversity_radius: float = 0.3,
                max_dist: Optional[float] = None) -> List[Dict[str, Any]]:
        """
        Generates counterfactual explanations for one or more instances.
        
        Args:
            X_input: The instance(s) to explain.
            num_cf: Number of counterfactuals to generate per instance.
            diversity_radius: Minimum L2 distance in delta-space (ICA component space) between generated CFs.
            max_dist: The maximum acceptable L2 distance (in feature space, unmasked features only) 
                      for a successful counterfactual. If None, uses the value from the config ('MAX_DIST').
        
        Returns:
            A list of dictionaries, each representing one counterfactual explanation.
        """
        if not self._fitted:
             raise ValueError("Explainer must be fitted (call .fit(X, y)) before calling explain().")
        
        # Use config value if max_dist is not provided in the call
        final_max_dist = self.config['MAX_DIST'] if max_dist is None else max_dist

        # Convert input to a numpy array of encoded features
        if isinstance(X_input, pd.DataFrame):
            X_input_aligned = X_input[self.feature_names]
            X_test_np = X_input_aligned.values.astype(np.float64)
        elif isinstance(X_input, np.ndarray):
            X_test_np = X_input.astype(np.float64)
            if X_test_np.ndim == 1:
                X_test_np = X_test_np.reshape(1, -1)
            if X_test_np.shape[1] != len(self.feature_names):
                raise ValueError(f"Input array has {X_test_np.shape[1]} features, but explainer was fitted with {len(self.feature_names)}.")
        else:
            raise TypeError("X_input must be a pandas DataFrame or a numpy array.")

        final_explanations = []
        
        for i_instance, instance in enumerate(X_test_np):
            # 1. Prepare instance and predict original class
            instance_unmasked = instance[self.unmasked_indices]
            instance_masked = instance[self.masked_indices]
                 
            S_instance = self.ica.transform(instance_unmasked.reshape(1, -1))[0] if instance_unmasked.size > 0 else np.empty(0)
            
            instance_masked_combined = instance_masked.reshape(1, -1) if instance_masked.size > 0 else np.empty((1, 0))
            instance_combined = np.hstack((S_instance.reshape(1, -1), instance_masked_combined))
            
            original_pred_idx = self.classifier.predict(instance_combined)[0]
            original_pred_class = self.preprocessor.target_encoder.inverse_transform([original_pred_idx])[0]
            
            # Determine target class (the opposite of the predicted class)
            target_class_idx = 0 if original_pred_idx == 1 else 1
            target_class = self.preprocessor.target_encoder.inverse_transform([target_class_idx])[0]

            found_cf_deltas = []
            
            # 2. CF Generation Loop
            for cf_idx in range(num_cf):
                start_time = time.time()
                
                # Pass the final_max_dist value for filtering
                X_cf, delta_selected = self._run_optimization(
                    instance, S_instance, instance_masked, target_class_idx,
                    final_max_dist, found_cf_deltas, diversity_radius
                )
                
                generation_time = time.time() - start_time
                
                # 3. Format and Log Results
                cf_row = {
                    'Original_Input_Index': i_instance,
                    'Original_Predicted_Class': original_pred_class,
                    'Target_Class': target_class,
                    'Counterfactual_ID': cf_idx + 1,
                    'Generation_Time_s': generation_time
                }
                
                original_df = self.preprocessor.inverse_transform_features(instance.reshape(1, -1))
                cf_row.update({f'Original_Feature_{name}': original_df[name].iloc[0] for name in self.feature_names})

                if X_cf is not None:
                    # Success
                    found_cf_deltas.append(delta_selected)
                    cf_df = self.preprocessor.inverse_transform_features(X_cf.reshape(1, -1))
                    
                    X_cf_unmasked = X_cf[self.unmasked_indices]
                    X_cf_masked = X_cf[self.masked_indices]
                    S_cf = self.ica.transform(X_cf_unmasked.reshape(1, -1))
                    
                    X_cf_masked_combined = X_cf_masked.reshape(1, -1) if X_cf_masked.size > 0 else np.empty((1, 0))
                    X_cf_combined = np.hstack((S_cf, X_cf_masked_combined))
                    
                    cf_pred_idx = self.classifier.predict(X_cf_combined)[0]
                    cf_pred_class = self.preprocessor.target_encoder.inverse_transform([cf_pred_idx])[0]
                    cf_target_proba = self.classifier.predict_proba(X_cf_combined)[0][target_class_idx] 
                    success = (cf_pred_idx == target_class_idx)
                    
                    distance = np.linalg.norm(X_cf[self.unmasked_indices] - instance_unmasked, ord=2)

                    cf_row.update({
                        'CF_Predicted_Class': cf_pred_class,
                        'CF_Target_Proba': cf_target_proba,
                        'L2_Distance': distance,
                        'Success': success
                    })
                    cf_row.update({f'Counterfactual_Feature_{name}': cf_df[name].iloc[0] for name in self.feature_names})
                else:
                    # Failure
                    cf_row.update({
                        'CF_Predicted_Class': original_pred_class,
                        'CF_Target_Proba': np.nan,
                        'L2_Distance': np.inf,
                        'Success': False
                    })
                    cf_row.update({f'Counterfactual_Feature_{name}': original_df[name].iloc[0] for name in self.feature_names})

                final_explanations.append(cf_row)

        return final_explanations