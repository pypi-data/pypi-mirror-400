# 📦 DEALA --- *Differentiated Economic Assessment in a Life cycle-oriented Analysis*

**DEALA** is a Python package developed to perform comprehensive and
differentiated **economic assessments** within **Life Cycle
(Sustainability) Assessment (LC(S)A)** or **Life Cycle Costing (LCC)**.\
It integrates economic data, provides three predefined economic life
cycle impact assessment methods, and extends existing LCA frameworks
such as [Brightway2](https://brightway.dev/) with economic databases and
characterization models.

------------------------------------------------------------------------

## 📚 Further Information

Detailed information about the DEALA method can be found in the
following scientific publication:

👉 https://doi.org/10.1111/jiec.13584

> Popien, J.-L., Barke, A., Ginster, R., Striecks, T., Thies, C., &
> Spengler, T. S. (2024).\
> **DEALA --- A novel economic life cycle impact assessment method for
> differentiated economic assessments in the context of life cycle
> sustainability assessments.**\
> *Journal of Industrial Ecology*. https://doi.org/10.1111/jiec.13584

### 📘 Doctoral Thesis (German only)

Additional background, theoretical derivations, and detailed data
structures can be found in the dissertation:

👉 https://link.springer.com/book/9783658500016\
*(German language)*

------------------------------------------------------------------------

## 🚀 Key Features

1.  **Three economic LCIA methods**\
    DEALA-Cost, DEALA-Profit, and DEALA-Invest.

2.  **Integrated marketsphere database**\
    Contains economic flows enabling economic impact calculations
    directly.

3.  **Support for Life Cycle Sustainability Assessments (LCSA)**\
    Unified environmental, social, and economic assessment.

4.  **Case studies & example notebooks**

    -   `pan_production.ipynb` -- main worked example\
    -   `regioinvent.ipynb` -- regionalized modeling with Regiopremise +
        efficient database generation\
    -   `calculation_results.ipynb` -- computing results & verifying
        correct setup

5.  **Example data and templates**\
    Useful datasets to support typical DEALA workflows.

6.  **Regionalized and time-dependent assessments**\
    Including scenario-specific and temporally resolved economic
    parameters.

------------------------------------------------------------------------

# 🏁 Getting Started

## 🔧 Installation Options

DEALA can be installed using **pip** or the recommended **uv-based
setup**.

------------------------------------------------------------------------

### ✔ Option A --- Install via pip

``` bash
pip install deala
```

------------------------------------------------------------------------

### ✔ Option B --- Recommended installation using uv (Astral)

### 1️⃣ Install uv

👉 https://docs.astral.sh/uv/getting-started/installation/

------------------------------------------------------------------------

### 2️⃣ Additional steps for macOS

1.  Install **Homebrew**\
    👉 https://brew.sh/

2.  Install required packages:

``` bash
brew install swig suite-sparse pkg-config
```

3.  Set compiler flag:

``` bash
export CFLAGS="$CFLAGS -Wno-int-conversion"
```

------------------------------------------------------------------------

### 3️⃣ Create an empty project directory

``` bash
mkdir deala_env
cd deala_env
code .
```

------------------------------------------------------------------------

### 4️⃣ Initialize the project using uv

``` bash
uv init --python 3.11.8
```

------------------------------------------------------------------------

### 5️⃣ Add DEALA to the environment

``` bash
uv add deala
```

------------------------------------------------------------------------

### 6️⃣ (Optional) Add Regiopremise for regionalized inventories

``` bash
uv add "regioinvent @ git+https://github.com/matthieu-str/Regiopremise"
```

------------------------------------------------------------------------

# 🧪 Example: Loading DEALA & Importing Databases

``` python
import deala as de
from deala import deala_io

deala_io_instance = deala_io()
```

------------------------------------------------------------------------

## 1. Setup DEALA

Loads the marketsphere database and the DEALA LCIA methods.

``` python
deala_io_instance.deala_setup(overwrite=True)
```

------------------------------------------------------------------------

## 2. Import DEALA activities

Uses predefined datasets (labor, construction, materials, etc.) and
generates scenario-dependent databases.

``` python
deala_io_instance.import_DEALA_activities_fast(
    base_year,
    dict_scenarios,
    directory_deala,
    price_calculation=price_calculation_method,
    method_calc_r=method_calculation_real_prices,
    modus=None
)
```

**Import PPP-based regionalized material prices:**

``` python
deala_io_instance.import_PPP_DEALA_activities(FP_material_regionalized)
```

------------------------------------------------------------------------

## 3. Create default DEALA activities

Creates activities with unknown ex-ante prices (investment-dependent,
cost-based, etc.).

``` python
deala_io_instance.create_default_DEALA_activities_fast(
    "DEALA_activities_",
    dict_scenarios,
    overwrite=False
)
```

------------------------------------------------------------------------

# 📄 License

BSD 3-Clause License

------------------------------------------------------------------------

# 🙋 Support

For questions, suggestions, or contributions, please open an issue on
GitHub or contact the development team.
