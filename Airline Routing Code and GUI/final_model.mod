## Program 2

param N;
param T;
param no_of_lats;
param no_of_longs;
param connected {m in 1..N, n in 1..N};
param city_coordinates {m in 1..N, 1..2};
param bad_weather {i in 1..(no_of_lats+2), j in 1..(no_of_longs+2)};

var waypoint {m in 1..N, n in 1..N, t in 1..T, i in 1..(no_of_lats+2), j in 1..(no_of_longs+2)} binary;

minimize Distance:
	sum {m in 1..N, n in 1..N, t in 1..T, i in 1..(no_of_lats+2), j in 1..(no_of_longs+2)} waypoint[m, n, t, i, j];


# Eliminate unconnected cities
subject to Unconnectedness {m in 1..N, n in 1..N, t in 1..T}:
	0 = if (connected[m, n] = 0) then (sum {i in 1..(no_of_lats+2), j in 1..(no_of_longs+2)} waypoint[m, n, t, i, j]) else 0;

# At any timestep, at most one node should be selected for a particular route
subject to Only_one_node_at_time_t {m in 1..N, n in 1..N, t in 1..T}:
	sum {i in 1..(no_of_lats+2), j in 1..(no_of_longs+2)} waypoint[m, n, t, i, j] <= 1;

# Starting and ending points must be marked
subject to Endpoints_start {m in 1..N, n in 1..N}:
	0 = if (connected[m, n] = 1) then (waypoint[m, n, 1, city_coordinates[m, 1], city_coordinates[m, 2]] - 1) else 0;
subject to Endpoints_end {m in 1..N, n in 1..N}:
	0 = if (connected[m, n] = 1) then ((sum {t in 1..T} waypoint[m, n, t, city_coordinates[n, 1], city_coordinates[n, 2]]) - 1) else 0;

# Consecutiveness must be maintained between any 2 timesteps
subject to Continuity {m in 1..N, n in 1..N, t in 1..(T-1), i in 2..(no_of_lats+1), j in 2..(no_of_longs+1)}:
	0 = if (waypoint[m, n, t, i, j] = 1 and not (i = city_coordinates[n, 1] and j = city_coordinates[n, 2])) 
			then (waypoint[m, n, t+1, i+1, j] + waypoint[m, n, t+1, i-1, j] + waypoint[m, n, t+1, i, j+1] + waypoint[m, n, t+1, i, j-1] - 1)
		else if (waypoint[m, n, t, i, j] = 1 and (i = city_coordinates[n, 1] and j = city_coordinates[n, 2]))
			then (waypoint[m, n, t+1, i+1, j] + waypoint[m, n, t+1, i-1, j] + waypoint[m, n, t+1, i, j+1] + waypoint[m, n, t+1, i, j-1])
		else 0;

# Make edge waypoints 0
subject to Edges_i1 {m in 1..N, n in 1..N, t in 1..T}:
	sum {i in 1..(no_of_lats+2)} waypoint[m, n, t, i, 1] = 0;
subject to Edges_i2 {m in 1..N, n in 1..N, t in 1..T}:
	sum {i in 1..(no_of_lats+2)} waypoint[m, n, t, i, (no_of_longs+2)] = 0;
subject to Edges_j1 {m in 1..N, n in 1..N, t in 1..T}:
	sum {j in 1..(no_of_longs+2)} waypoint[m, n, t, 1, j] = 0;
subject to Edges_j2 {m in 1..N, n in 1..N, t in 1..T}:
	sum {j in 1..(no_of_longs+2)} waypoint[m, n, t, (no_of_lats+2), j] = 0;

# No repeating paths
subject to No_retraces{m in 1..N, n in 1..N, i in 1..(no_of_lats+2), j in 1..(no_of_longs+2)}:
    sum {t in 1..T} waypoint[m, n, t, i, j] <= 1;

# Avoid collisions
subject to Collisions{t in 2..T, i in 1..(no_of_lats+2), j in 1..(no_of_longs+2)}:
	sum {m in 1..N, n in 1..N} waypoint[m, n, t, i, j] <= 1;

# Avoid bad weather
subject to Bad_weather{m in 1..N, n in 1..N, t in 1..T, i in 1..(no_of_lats+2), j in 1..(no_of_longs+2)}:
	0 = if (bad_weather[i, j] = 1) then waypoint[m, n, t, i, j] else 0;