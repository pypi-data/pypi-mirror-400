class Model(Discipline):

    def __init__(self,
        nb_points: int = 5,
        mesh_x_shift: float = 0.0,
        mesh_ratio: float = 1.0,
        is_decreasing_mesh: bool = False,
    ):
        super().__init__()

        self.nb_points = nb_points
        self.mesh_x_shift = mesh_x_shift
        self.mesh_ratio = mesh_ratio
        self.is_decreasing_mesh = is_decreasing_mesh

    def __init__(self) -> None:
        super().__init__()
        self.input_grammar.update_from_names(["x"])
        self.output_grammar.update_from_names(["y", "mesh"])
        self.default_input_data = {
            "x": array([0.0]),
        }

    def _run(self, input_data: StrKeyMapping) -> StrKeyMapping | None:
        x_input = input_data["x"]
        y_mesh = linspace(0, 1, self.nb_points) * self.mesh_ratio + self.mesh_x_shift
        if self.is_decreasing_mesh:
            y_mesh = -y_mesh
        y = full((self.nb_points), 1.0)
        return {"y_mesh": y_mesh, "y": y}