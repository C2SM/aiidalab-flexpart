import ipywidgets as widgets

style = {'description_width': 'initial'}

class Releases(widgets.VBox):
    def __init__(self):
        self.particles_per_release = widgets.IntText(
            value=50000,
            description='particles_per_release',
            disabled=False,
            style=style
        )
        self.mass_per_release = widgets.Text(
            value='1',
            placeholder='mass_per_release',
            description='mass_per_release',
            disabled=False,style=style 
        )
        self.list_of_species = widgets.Text(
            value='24',
            placeholder='list_of_species',
            description='list_of_species',
            disabled=False,style=style 
        )
        self.children=[self.particles_per_release,
                  self.mass_per_release,
                  self.list_of_species
        ]
        super().__init__(children = self.children)
        
    def fill_dict(self):
        return {self.particles_per_release.description:self.particles_per_release.value,
                self.mass_per_release.description: self.mass_per_release.value.split(','),
                self.list_of_species.description: self.list_of_species.value.split(',') } 
    
    def update(self, dict_):
        for param in self.params:
            param.value = dict_[param.description]
    