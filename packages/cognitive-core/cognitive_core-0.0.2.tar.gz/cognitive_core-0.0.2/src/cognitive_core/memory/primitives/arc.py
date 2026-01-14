"""ARC-AGI domain primitives for grid manipulation.

These primitives represent common operations needed for ARC-AGI tasks,
based on patterns identified in successful solutions.
"""

from __future__ import annotations

from cognitive_core.core.types import CodeConcept


class ARCPrimitiveLoader:
    """Load ARC-AGI grid manipulation primitives.

    Provides a set of fundamental operations for working with ARC grids,
    including object detection, transformations, and color operations.

    Example:
        ```python
        loader = ARCPrimitiveLoader()
        primitives = loader.load()
        rotate = primitives["arc_rotate_90"]
        ```
    """

    def load(self) -> dict[str, CodeConcept]:
        """Load all ARC primitives.

        Returns:
            Dict mapping primitive ID to CodeConcept.
        """
        return {
            "arc_get_objects": CodeConcept(
                id="arc_get_objects",
                name="get_objects",
                description="Extract connected components (objects) from a grid based on color connectivity",
                code="""def get_objects(grid: np.ndarray, background: int = 0) -> list[Object]:
    '''Find all connected components in grid, excluding background color.'''
    # Uses flood-fill to identify connected regions
    ...""",
                signature="(grid: np.ndarray, background: int = 0) -> list[Object]",
                examples=[
                    ("grid with 2 colored regions", "list of 2 Object instances"),
                    ("empty grid", "empty list"),
                ],
                source="primitive",
            ),
            "arc_flood_fill": CodeConcept(
                id="arc_flood_fill",
                name="flood_fill",
                description="Fill a connected region starting from a point with a new color",
                code="""def flood_fill(grid: np.ndarray, start: tuple[int, int], color: int) -> np.ndarray:
    '''Fill connected region of same color starting from start position.'''
    ...""",
                signature="(grid: np.ndarray, start: tuple[int, int], color: int) -> np.ndarray",
                examples=[
                    ("grid, (0, 0), 5", "grid with region starting at (0,0) filled with color 5"),
                ],
                source="primitive",
            ),
            "arc_rotate_90": CodeConcept(
                id="arc_rotate_90",
                name="rotate_90",
                description="Rotate a grid 90 degrees clockwise",
                code="""def rotate_90(grid: np.ndarray) -> np.ndarray:
    '''Rotate grid 90 degrees clockwise.'''
    return np.rot90(grid, k=-1)""",
                signature="(grid: np.ndarray) -> np.ndarray",
                examples=[
                    ("[[1,2],[3,4]]", "[[3,1],[4,2]]"),
                ],
                source="primitive",
            ),
            "arc_rotate_180": CodeConcept(
                id="arc_rotate_180",
                name="rotate_180",
                description="Rotate a grid 180 degrees",
                code="""def rotate_180(grid: np.ndarray) -> np.ndarray:
    '''Rotate grid 180 degrees.'''
    return np.rot90(grid, k=2)""",
                signature="(grid: np.ndarray) -> np.ndarray",
                examples=[
                    ("[[1,2],[3,4]]", "[[4,3],[2,1]]"),
                ],
                source="primitive",
            ),
            "arc_rotate_270": CodeConcept(
                id="arc_rotate_270",
                name="rotate_270",
                description="Rotate a grid 270 degrees clockwise (90 degrees counter-clockwise)",
                code="""def rotate_270(grid: np.ndarray) -> np.ndarray:
    '''Rotate grid 270 degrees clockwise.'''
    return np.rot90(grid, k=1)""",
                signature="(grid: np.ndarray) -> np.ndarray",
                examples=[
                    ("[[1,2],[3,4]]", "[[2,4],[1,3]]"),
                ],
                source="primitive",
            ),
            "arc_mirror_horizontal": CodeConcept(
                id="arc_mirror_horizontal",
                name="mirror_horizontal",
                description="Mirror a grid horizontally (flip left-right)",
                code="""def mirror_horizontal(grid: np.ndarray) -> np.ndarray:
    '''Mirror grid horizontally (flip left-right).'''
    return np.fliplr(grid)""",
                signature="(grid: np.ndarray) -> np.ndarray",
                examples=[
                    ("[[1,2],[3,4]]", "[[2,1],[4,3]]"),
                ],
                source="primitive",
            ),
            "arc_mirror_vertical": CodeConcept(
                id="arc_mirror_vertical",
                name="mirror_vertical",
                description="Mirror a grid vertically (flip top-bottom)",
                code="""def mirror_vertical(grid: np.ndarray) -> np.ndarray:
    '''Mirror grid vertically (flip top-bottom).'''
    return np.flipud(grid)""",
                signature="(grid: np.ndarray) -> np.ndarray",
                examples=[
                    ("[[1,2],[3,4]]", "[[3,4],[1,2]]"),
                ],
                source="primitive",
            ),
            "arc_get_background_color": CodeConcept(
                id="arc_get_background_color",
                name="get_background_color",
                description="Determine the background color of a grid (most common color or edge color)",
                code="""def get_background_color(grid: np.ndarray) -> int:
    '''Find the background color (most frequent or edge color).'''
    from collections import Counter
    colors = Counter(grid.flatten())
    return colors.most_common(1)[0][0]""",
                signature="(grid: np.ndarray) -> int",
                examples=[
                    ("grid with mostly 0s", "0"),
                    ("grid with mostly 5s", "5"),
                ],
                source="primitive",
            ),
            "arc_get_colors": CodeConcept(
                id="arc_get_colors",
                name="get_colors",
                description="Get the set of unique colors present in a grid",
                code="""def get_colors(grid: np.ndarray) -> set[int]:
    '''Return set of unique colors in the grid.'''
    return set(grid.flatten().tolist())""",
                signature="(grid: np.ndarray) -> set[int]",
                examples=[
                    ("[[0,1],[2,0]]", "{0, 1, 2}"),
                ],
                source="primitive",
            ),
            "arc_crop_to_content": CodeConcept(
                id="arc_crop_to_content",
                name="crop_to_content",
                description="Crop a grid to the bounding box of non-background content",
                code="""def crop_to_content(grid: np.ndarray, background: int = 0) -> np.ndarray:
    '''Crop grid to smallest rectangle containing all non-background cells.'''
    rows = np.any(grid != background, axis=1)
    cols = np.any(grid != background, axis=0)
    return grid[rows][:, cols]""",
                signature="(grid: np.ndarray, background: int = 0) -> np.ndarray",
                examples=[
                    ("5x5 grid with 2x2 content", "2x2 grid"),
                ],
                source="primitive",
            ),
            "arc_scale_grid": CodeConcept(
                id="arc_scale_grid",
                name="scale_grid",
                description="Scale a grid by a factor (each cell becomes factor x factor cells)",
                code="""def scale_grid(grid: np.ndarray, factor: int) -> np.ndarray:
    '''Scale grid by integer factor.'''
    return np.repeat(np.repeat(grid, factor, axis=0), factor, axis=1)""",
                signature="(grid: np.ndarray, factor: int) -> np.ndarray",
                examples=[
                    ("[[1,2]], factor=2", "[[1,1,2,2],[1,1,2,2]]"),
                ],
                source="primitive",
            ),
            "arc_tile_pattern": CodeConcept(
                id="arc_tile_pattern",
                name="tile_pattern",
                description="Tile a pattern to fill a target size",
                code="""def tile_pattern(pattern: np.ndarray, rows: int, cols: int) -> np.ndarray:
    '''Tile pattern to create grid of target size.'''
    ph, pw = pattern.shape
    return np.tile(pattern, (rows // ph + 1, cols // pw + 1))[:rows, :cols]""",
                signature="(pattern: np.ndarray, rows: int, cols: int) -> np.ndarray",
                examples=[
                    ("2x2 pattern, 6, 6", "6x6 grid with pattern tiled"),
                ],
                source="primitive",
            ),
        }
