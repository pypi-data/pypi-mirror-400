from mikecore.DfsuFile import DfsuFile
import numpy as np
from matplotlib.tri import Triangulation

from .utils import Utils, Constants

class DfsuUtils:
    def __init__(self, fname: str) -> None:
        self.fname = fname
        self.dfsu = DfsuFile.Open(self.fname)
        
    @property
    def n_items(self) -> int:
        return len(self.dfsu.ItemInfo)

    @property
    def n_timesteps(self) -> int:
        return self.dfsu.NumberOfTimeSteps

    @property
    def n_nodes(self) -> int:
        return self.dfsu.NumberOfNodes

    @property
    def n_elements(self) -> int:
        return self.dfsu.NumberOfElements

    @property
    def n_layers(self) -> int:
        return self.dfsu.NumberOfLayers

    @property
    def n_nodes_2d(self) -> int:
        """
        Get the number of nodes in the 2D horizontal mesh.
        
        Returns:
            int: The number of nodes in the bottom layer of the 3D domain.
        """
        return self.n_nodes // (self.n_layers + 1)
    
    @property
    def n_elements_2d(self) -> int:
        """
        Get the number of elements in the 2D horizontal mesh.
        
        Returns:
            int: The number of elements in the bottom layer of the 3D domain.
        """
        return self.et_2d.shape[0]

    @property
    def nc(self) -> np.ndarray:
        """
        Get the node coordinates of the dfsu file.
        
        Returns:
            np.ndarray: An array of shape (n_nodes, 3) containing the X, Y, and Z coordinates of the nodes.
        """
        return np.stack((self.dfsu.X, self.dfsu.Y, self.dfsu.Z), axis=1)
    node_coordinates = nc  # Alias for backward compatibility

    @property
    def et(self) -> np.ndarray:
        """
        Get the element connectivity of the dfsu file.
        
        Returns:
            np.ndarray: An array of shape (n_elements, 3) containing the node indices for each element.
        """
        return np.stack(self.dfsu.ElementTable, axis=1).T - 1
    element_table = et  # Alias for backward compatibility

    @property
    def model_times(self) -> np.ndarray:
        """
        Get the model times of the dfsu file.
        
        Returns:
            np.ndarray: An array of datetime64 objects representing the model times.
        """
        return np.array(self.dfsu.GetDateTimes()).astype('datetime64[ns]')
    times = model_times  # Alias for backward compatibility
    timesteps = model_times  # Alias for backward compatibility
    datetimes = model_times  # Alias for backward compatibility

    @property
    def nc_2d(self) -> np.ndarray:
        """
        Get the 2D node coordinates over a horizontal plane in the 3D domain.
        
        Returns:
            np.ndarray: An array of shape (n_nodes, 2) containing the X and Y coordinates of the bottom layer nodes.
        """
        return self._get_bottom_layer_nodes(self.nc, self.n_layers)
    node_coordinates_2d = nc_2d  # Alias for backward compatibility

    @staticmethod
    def _get_bottom_layer_nodes(nc: np.ndarray, n_layers: int) -> np.ndarray:
        return nc[np.arange(0, nc.shape[0], n_layers + 1), :2]  # Only X, Y

    @property
    def et_2d(self) -> np.ndarray:
        """
        Get the element table for 2D horizontal mesh.
        
        Returns:
            np.ndarray: An array of shape (n_elements, 3) containing the node indices for each 2D element.
        """
        return self._get_bottom_triangles(self.et, self.n_layers)
    element_table_2d = et_2d  # Alias for backward compatibility
    
    @staticmethod
    def _get_bottom_triangles(et: np.ndarray, n_layers: int) -> np.ndarray:
        bottom_layer_elements = et[::n_layers]  # every n_layers-th element is the bottom prism
        bottom_triangles = bottom_layer_elements[:, :3] // (n_layers + 1)  # get node indices in bottom layer
        return bottom_triangles
    
    @property
    def tri2d(self) -> Triangulation:
        """
        Get the 2D triangulation of the mesh.
        
        Returns:
            Triangulation: A triangulation object for the 2D mesh.
        """
        return Triangulation(self.nc_2d[:, 0], self.nc_2d[:, 1], self.et_2d)
    tri = tri2d  # Alias for backward compatibility
    triangles = tri2d  # Alias for backward compatibility

    @property
    def sigma_layer_fractions(self) -> np.ndarray:
        """
        Compute the thickness fractions of each sigma layer across the domain.
        Returns
        -------
        np.ndarray
            An array of shape (n_layers,) containing the thickness fractions for each sigma layer.
        """
        z = self.nc[:, 2].reshape(self.n_nodes_2d, self.n_layers + 1)

        total_depth = z[:, -1] - z[:, 0]
        with np.errstate(divide='ignore', invalid='ignore'):
            layer_thicknesses = np.diff(z, axis=1) / total_depth[:, None]
            layer_thicknesses[~np.isfinite(layer_thicknesses)] = 0  # handle 0 division or nan

        return np.mean(layer_thicknesses, axis=0)
    sigma_fractions = sigma_layer_fractions  # Alias for backward compatibility

    def find_elements_2d(self, x: np.ndarray = None, y: np.ndarray = None) -> np.ndarray:
        """
        Find the element indices for given x, y coordinates in the 2D mesh.
        
        Parameters:
            x (np.ndarray): X coordinates.
            y (np.ndarray): Y coordinates.
            xy (np.ndarray, optional): If provided, will use these coordinates instead of x and y.
        
        Returns:
            np.ndarray: An array of element indices corresponding to the input coordinates.
        """
        x = np.array(x).flatten()
        y = np.array(y).flatten()    
        finder = self.tri2d.get_trifinder()
        return finder(x, y)
    
    def find_elements_vertical(self, x: np.ndarray = None, y: np.ndarray = None) -> np.ndarray:
        """
        Find the element indices in the vertical direction for given x, y coordinates.
        Parameters:
            x (np.ndarray): X coordinates.
            y (np.ndarray): Y coordinates.
            xy (np.ndarray, optional): If provided, will use these coordinates instead of x and y.
        Returns:
            np.ndarray: An array of element indices corresponding to the input coordinates.
        """
        x = np.array(x).flatten()
        y = np.array(y).flatten()    
        elements_2d = self.find_elements_2d(x, y)
        n_layers = self.n_layers
        return np.array([np.arange(i * n_layers, (i + 1) * n_layers) for i in elements_2d])
    
    def find_bracketing_timesteps(self, times: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        """
        Find the indices of the model times that bracket the given times.
        Parameters
        ----------
        times : np.ndarray
            An array of times for which to find the bracketing indices.
        Returns
        -------
        tuple[np.ndarray, np.ndarray]
            Two arrays containing the indices of the model times immediately before and after each time in `times`.
        """
        model_times = self.times
        if isinstance(times, np.datetime64):
            times = np.array(times, dtype='datetime64[ns]')
        # Find index of the first model_time > each traj_time
        after_indices = np.searchsorted(model_times, times, side='right')
        before_indices = after_indices - 1

        # Clamp to valid index range
        before_indices = np.clip(before_indices, 0, len(model_times) - 1)
        after_indices = np.clip(after_indices, 0, len(model_times) - 1)

        return before_indices, after_indices

    def get_elevation(self, x: np.ndarray = None, y: np.ndarray = None, xy: np.ndarray = None, loc: str = "bottom") -> np.ndarray:
        """
        Interpolate the bed elevation at given x, y coordinates.
        Parameters
        ----------
        x : np.ndarray, optional
            X coordinates. If provided, y must also be provided.
        y : np.ndarray, optional
            Y coordinates. If provided, x must also be provided.
        xy : np.ndarray, optional
            Combined X and Y coordinates. If provided, x and y will be ignored.
        Returns
        -------
        np.ndarray
            An array of bed elevations at the specified coordinates.
        """
        if xy is not None:
            xy = np.array(xy)
            x, y = xy[:, 0], xy[:, 1]
        else:
            x = np.array(x).flatten()
            y = np.array(y).flatten()    
        addition = self.n_layers if loc.lower() == "surface" else 0
        bottom_layer_nodes = self.nc[::self.n_layers + 1, :2]
        xy = np.column_stack((x, y))
        elevations = []
        for idx, (x, y) in zip(self.et_2d, xy):
            node_ids = self.et_2d[idx]
            node_coords = bottom_layer_nodes[node_ids]  # shape (3, 2)
            # Get bottom node indices in nc
            target_node_ids = node_ids * (self.n_layers + 1) + addition
            node_zs = self.nc[target_node_ids, 2]

            dists = np.linalg.norm(node_coords - np.array([x, y]), axis=1)
            weights = 1 / (dists + 1e-8)
            weights /= np.sum(weights)

            elevations.append(np.dot(weights, node_zs))

        return np.array(elevations)

    def get_layer_elevations(self, x: np.ndarray = None, y: np.ndarray = None, xy: np.ndarray = None) -> np.ndarray:
        """
        Get the elevations of all layers at given x, y coordinates.
        
        Parameters
        ----------
        x : np.ndarray, optional
            X coordinates. If provided, y must also be provided.
        y : np.ndarray, optional
            Y coordinates. If provided, x must also be provided.
        xy : np.ndarray, optional
            Combined X and Y coordinates. If provided, x and y will be ignored.
        
        Returns
        -------
        np.ndarray
            An array of shape (n_points, n_layers) containing the elevations for each layer at the specified coordinates.
        """
        if xy is not None:
            xy = np.array(xy)
            x, y = xy[:, 0], xy[:, 1]
        else:
            x = np.array(x).flatten()
            y = np.array(y).flatten()
        surface = self.get_elevation(x, y, xy, loc="surface")
        bottom = self.get_elevation(x, y, xy, loc="bottom")
        water_depth = surface - bottom  # shape (n_points,)
        layer_depths = np.outer(water_depth, self.sigma_layer_fractions)  # (n_points, n_layers)
        layer_elevations = bottom[:, None] + np.cumsum(layer_depths, axis=1)
        return layer_elevations
    
    def extract_transect(self, x: np.ndarray, y: np.ndarray, t: np.ndarray, item_number: int) -> np.ndarray:
        """
        Extract a transect from the model data.
        
        Parameters
        ----------
        x : np.ndarray
            Array of x-coordinates.
        y : np.ndarray
            Array of y-coordinates.
        t : np.ndarray
            Array of timestamps.
        
        Returns
        -------
        np.ndarray
            An array containing the extracted transect data.
        """
        if item_number < 1 or item_number > self.n_items:
            raise ValueError(f"Item number must be between 1 and {self.n_items}, got {item_number}.")
        vertical_columns = self.find_elements_vertical(x=x, y=y)
        t = t.astype('datetime64[ns]')
        before_indices, after_indices = self.find_bracketing_timesteps(times=t)

        raw_data = []
        for i in range(len(t)):
            before_data = self.dfsu.ReadItemTimeStep(item_number, before_indices[i]).Data
            after_data = self.dfsu.ReadItemTimeStep(item_number, after_indices[i]).Data
            before_data = before_data[vertical_columns[i, :]]
            after_data = after_data[vertical_columns[i, :]]
            row_data = np.column_stack((before_data, after_data))
            raw_data.append(row_data)
        raw_data = np.array(raw_data)
        n_points, n_layers, _ = raw_data.shape
        
        data = np.empty((n_points, n_layers), dtype=float)
        model_times = self.model_times
        for i in range(n_points):
            t0 = model_times[before_indices[i]]
            t1 = model_times[after_indices[i]]
            tt = t[i]

            # Avoid division by zero if t0 == t1 (e.g., on exact timestamp)
            if t0 == t1:
                w0, w1 = 0.5, 0.5
            else:
                total = (t1 - t0) / np.timedelta64(1, 's')
                w0 = (t1 - tt) / np.timedelta64(1, 's') / total
                w1 = (tt - t0) / np.timedelta64(1, 's') / total

            vals = raw_data[i]  # shape (n_layers, 2)
            data[i] = vals[:, 0] * w0 + vals[:, 1] * w1
        return data, t, vertical_columns
    