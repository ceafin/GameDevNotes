Since `TerrainChunk` extends `StaticBody2D`, the physics engine gives you the chunk reference automatically when a collision happens. There are two common approaches:

## 1. Missile as `Area2D` (simplest)

Give the missile an `Area2D` with a collision shape. Connect its `body_entered` signal:

The physics engine tells you _which_ `TerrainChunk` `StaticBody2D` the missile overlapped — no manual chunk lookup needed.

## 2. Missile as `RigidBody2D` or using a raycast

If using a raycast to detect ground impact:

```swift
if raycast.is_colliding():
    var collider = raycast.get_collider()
    if collider is TerrainChunk:
        var hit_point = raycast.get_collision_point()
        var local_hit = collider.to_local(hit_point)
        collider.apply_crater(local_hit.x, 16.0)
```

Each `TerrainChunk` is a `StaticBody2D` with a `CollisionPolygon2D` built from its height data (see [terrain_chunk.gd:39-45](vscode-file://vscode-app/usr/share/code/resources/app/out/vs/code/electron-browser/workbench/workbench.html)). Godot's physics automatically resolves which specific chunk body was hit, so `body` / `get_collider()` returns the exact `TerrainChunk` instance. Then `to_local()` converts the world-space impact point into chunk-local X, which is what `apply_crater()` expects.

## One caveat

If a crater straddles two chunks, you'd need to also apply it to the neighboring chunk. You could handle that in `Terrain` by finding the adjacent chunk when `local_x - radius < 0` or `local_x + radius > CHUNK_WIDTH`.