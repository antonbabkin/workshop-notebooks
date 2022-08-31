# Literate programming and interactive reporting with Jupyter notebooks

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/antonbabkin/workshop-notebooks/HEAD?urlpath=lab) |
[Documentation](https://antonbabkin.github.io/workshop-notebooks/)

This is an intermediate level workshop that will teach how to use Jupyter notebooks with Python for literate programming and interactive presentation of research results. I walk participants through steps of a mini research project of visualizing geospatial data, focusing on tools and methods of making results accessible, reproducible and interactive. This workshop uses economic, demographic and geographic data characterizing US communities that are freely and publicly available from the US Census Bureau website.

Prior programming and data analysis experience is recommended for full participation in the workshop. If you are new to Python, I recommend reading about [Jupyter](https://jupyter.org/) and [pandas](https://pandas.pydata.org/). This [book](https://jupyter4edu.github.io/jupyter-edu-book/) shows how to use Jupyter notebooks for teaching and learning, and [QuantEcon](https://quantecon.org/lectures/) lectures use Python for economics and finance and are also a good resource for beginners.

Workshop topics: 
- Jupyter notebooks and Markdown
- Jupytext and Git
- code organization, Python modules and packages
- static documentation with Quarto
- data retrieval via download and API
- data processing and analysis in `pandas`
- plotting with `matplotlib` and `plotly`
- building interactive interfaces with notebook widgets
- visualization of geospatial data, `geopandas`, `folium` and `ipyleaflet`
- hosting live notebooks on Binder and static documentation on GitHub Pages

This workshop has been conducted by Anton Babkin at:
- Department of Agricultural and Applied Economics, University of Wisconsin-Madison, August 29-30, 2022. Repository tag [`2022-08-29`](https://github.com/antonbabkin/workshop-notebooks/tree/2022-08-29).
- 2022 Data Science Research Bazaar, University of Wisconsin-Madison, February 9, 2022. Repository tag [`2022-02-09`](https://github.com/antonbabkin/workshop-notebooks/tree/2022-02-09). Video recording [here](https://www.youtube.com/watch?v=xWiLzdHSowk).

## Setup

You need a running Jupyter server in order to work with workshop notebooks. The easiest way is to launch a free cloud instance in [Binder](https://mybinder.org/). A more difficult (but more reliable) alternative is to create [conda](https://docs.conda.io/en/latest/) Python environment on your local computer.

### Using Binder

Click this [link](https://mybinder.org/v2/gh/antonbabkin/workshop-notebooks/HEAD?urlpath=lab) to launch a new Binder instance and connect to it from your browser, then open and run `nbs/index.md` notebook to test the environment and initialize paths. Ideal launch time is under 30 seconds, but it might take longer if the repository has been recently updated, because Binder will need to rebuild the environment from scratch.

Notice that Binder platform provides computational resources for free, and so limitations are in place and availability can not be guaranteed. Read [here](https://mybinder.readthedocs.io/en/latest/about/about.html#using-the-mybinder-org-service) about usage policy and available resources. Quarto tools for static HTML documentation generation will not be available.


### Local Python

This method requires some experience or readiness to read documentation. As reward, you will have persistent environment under your control that does not depend on cloud service availability. This is also a typical way to set up Python for data work.

1. Download and install latest [miniconda](https://docs.conda.io/en/latest/miniconda.html), following instructions for your operating system. Skip this step if you already have `conda` command line utility available in your terminal.

1. Install [mamba](https://mamba.readthedocs.io/en/latest/installation.html) into base environment.
    ```
    conda install mamba -n base -c conda-forge
    ```
    
1. (Windows) Enable "Developer mode" to allow symbolic links.  
Settings -> Update & Security -> For developers -> Developer mode

1. Install Git command line utility.

1. Open terminal and clone this repository into a folder of your choice (`git clone https://github.com/antonbabkin/workshop-notebooks.git`). Alternatively, [download](https://github.com/antonbabkin/workshop-notebooks/archive/refs/heads/main.zip) and unpack repository code as ZIP. If you want to practice building and hosting HTML documentation, you need to use a repository that you control. One way to do it is to fork this repository and then clone your copy.

1. In the terminal, navigate to the repository folder and create new [conda environment](https://conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html#creating-an-environment-from-an-environment-yml-file). Environment specification will be read from the `environment.yml` file, all required packages will be downloaded and installed. Using `mamba` for this will typically work better.
    ```
    cd workshop-notebooks
    mamba env create -f environment.yml
    ```

1. Activate the environment and start JupyterLab server. This will start a new Jupyter server and open Jupyter interface in a browser window.
    ```
    conda activate workshop-nbs-2022
    jupyter lab
    ```
    
1. In Jupyter, open and run `nbs/index.md` notebook to inivialize paths and test your environment. You will need to right-click the file and choose "Open With -> Notebook" to let Jupytext automatically create a notebook from markdown.

1. Install Quarto CLI for your operating system from [here](https://quarto.org/docs/get-started/).


## License

Project code is licensed under the [MIT license](LICENSE.md). All other content is licensed under the [Creative Commons Attribution 4.0 International license](https://creativecommons.org/licenses/by/4.0/).
