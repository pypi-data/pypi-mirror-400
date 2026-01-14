
<div align="center"><img src=https://gitlab.com/cerfacs/moonframe/raw/main/docs/images/moonframe.png width=90% alt="Moonframe's banner containing the logo, the title of the repo and a subtitle : d3.js visuals with Python."/></div>

<div align="center"><h1>Moonframe </h1></div>

<i>Moonframe is an open-source Python library that helps you create interactive graphs using <a href="https://d3js.org/">D3.js</a> without writing a single line of JavaScript.   
It’s built for quick data exploration and aims to be as simple and accessible as possible.</i>


## Main features
### Customizable charts without coding

Moonframe provides a clear interface that handles all customization. You can easily navigate between graph views to explore your dataset.

<div><img src=https://gitlab.com/cerfacs/moonframe/raw/main/docs/images/tuto_scatter/step2_custom_scatter.gif width=49% alt="Scatter plot demo. A menu on the left allows you to select the names of the columns you want to plot. You can change X,Y, size and color."/>
<img src=https://gitlab.com/cerfacs/moonframe/raw/main/docs/images/tuto_scatter/step3_custom_col.gif width=49% alt="Scatter plot demo. With the menu on the left, you can change the color palette of the chart."/></div>

### Interact with the data

Tooltips are available on all charts. They show details from your data when you hover over a point, and you can fully customize what they display. This can be helpful for getting quick insights. You can also highlight color groups on hover to spot trends more easily in your dataset.

<div><img src=https://gitlab.com/cerfacs/moonframe/raw/main/docs/images/tuto_scatter/step4_custom_tooltip.gif width=49% alt="Scatter plot demo. When the mouse hovers over a point, text appears describing the data associated with that point."/>
<img src=https://gitlab.com/cerfacs/moonframe/raw/main/docs/images/tuto_scatter/step5_group_by_color.gif width=49% alt="Scatter plot demo. An option allows you to group points that share the same colour group. As a result, when you hover over a point, all the points in the same group are shown."/></div>

### Easy to setup

Moonframe comes with a minimalist CLI: one command, one graph.
Your data just needs to be in CSV format; a widely used and simple standard in the data visualization community. You can also include Moonframe directly in any of your Python project!

## Getting started

> If you’re completely new to Python, the easiest way to begin is by following the <a href="docs/tutorials/getting_started.md">getting started tutorial</a>. This guide walks you through installing Moonframe and introduces a few essential basics. Give it a try!

### Requirements

* Web browser
* Python >= 3.7
* An internet connexion (just during graph generation)

### Installation

Install it from PyPI with : 

```
pip install moonframe
``` 

## Available charts

Click on any graph to get started!


### In Moonframe :


| <a href="https://gitlab.com/cerfacs/moonframe/-/blob/main/docs/tutorials/tuto_scatter.md?ref_type=heads"><img src="https://gitlab.com/cerfacs/moonframe/raw/main/docs/images/readme/scatter.png" width="100px;" alt="Screenshot of a scatter graph."><br> *Scatter* </a>|
|:--:|

### In Marauder's map :

<i>Marauder's map is an open-source Python helper tool to create visual representations of the internal structure of Python, C and Fortran packages.</i>


| <a href="https://gitlab.com/cerfacs/maraudersmap/-/blob/main/docs/howto/howto-treeshowjs.md?ref_type=heads"><img src="https://gitlab.com/cerfacs/moonframe/raw/main/docs/images/readme/circular_packing.png" width="100px;" alt="Screenshot of a circular packing graph."> <br> *Circular packing*</a>| <a href="https://gitlab.com/cerfacs/maraudersmap/-/blob/main/docs/howto/howto-cgshowjs.md?ref_type=heads"><img src="https://gitlab.com/cerfacs/moonframe/raw/main/docs/images/readme/network.png" width="100px;" alt="Screenshot of a network graph."> <br> *Network*</a> |
|:--:|:--:|
