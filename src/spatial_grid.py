"""Spatial grid for efficient neighbor queries."""


class SpatialGrid:
    """Uniform grid that maps entities to cells for O(n) neighbor lookups."""

    __slots__ = ("_cell_size", "_inv", "_cells")

    def __init__(self, cell_size: float) -> None:
        self._cell_size = cell_size
        self._inv = 1.0 / cell_size
        self._cells: dict[tuple[int, int], list] = {}

    def clear(self) -> None:
        self._cells.clear()

    def _key(self, x: float, y: float) -> tuple[int, int]:
        return int(x * self._inv), int(y * self._inv)

    def insert(self, entity) -> None:
        key = self._key(entity.position.x, entity.position.y)
        try:
            self._cells[key].append(entity)
        except KeyError:
            self._cells[key] = [entity]

    def get_neighbors(self, entity):
        """Yield entities in the same or adjacent 9 cells (excluding entity itself)."""
        cx, cy = self._key(entity.position.x, entity.position.y)
        cells = self._cells
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                bucket = cells.get((cx + dx, cy + dy))
                if bucket:
                    for other in bucket:
                        if other is not entity:
                            yield other
