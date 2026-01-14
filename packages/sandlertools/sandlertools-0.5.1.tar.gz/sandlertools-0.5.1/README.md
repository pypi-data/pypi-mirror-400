# Sandlertools

> A metapackage of utilities from Sandler's 5th ed.

Sandlertools combines several packages that implement computational tools based on _Chemical, Biochemical, and Engineering Thermodynamics_ (5th edition) by Stan Sandler (Wiley, USA). It should be used for educational purposes only.


## Installation 

Sandlertools is available via `pip`:

```sh
pip install sandlertools
```

This will install the following packages and wire their CLI's into `sandlertools`.
* `sandlerprops` -- pure component properties database
* `sandlersteam` -- steam tables
* `sandlercubics` -- real-gas cubic equations of state
* `sandlercorrespondingstates` -- corresponding-states chart reads
* `sandlerchemeq` -- chemical equilibrium calculations
* `sandlermisc` -- miscellaneous utilities

## Usage

### Command-line

The general structure of a `sandlertools` command is

```sh
$ sandlertools [<global-options>] <tool> [<tool-options>]
```
Currently available tools are
- `props`: Pure-component property lookup
- `cubic`: Cubic equations of state
- `steam`: Steam-tables
- `cs`: Corresponding states
- `chemeq`: Chemical equilibrium calculations

```sh
$ sandlertools --help
usage: sandlertools [-h] [-b | --banner | --no-banner] [--logging-level {None,info,debug,warning}] [-l LOG] <command> ...

Sandler Tools: A collection of computational tools based on Chemical, Biochemical, and Engineering Thermodynamics (5th edition) by Stan Sandler

options:
  -h, --help            show this help message and exit
  -b, --banner, --no-banner
                        toggle banner message
  --logging-level {None,info,debug,warning}
                        Logging level for messages written to diagnostic log
  -l LOG, --log LOG     File to which diagnostic log messages are written

subcommands:
  <command>
    props               query and manipulate thermophysical property data
    cubic               query and manipulate cubic equation of state calculations
    steam               work with steam tables and properties of water/steam
    cs                  work with corresponding states calculations
```

#### `sandlertools props`

Below is an example of using `sandlertools props` to look up pure-component properties for benzene.  We also show what
happens if you try to look up a compound that is not in the database.

```sh
$ sandlertools props show benzene
Properties of benzene (index 343):
  No        : 343
  Formula   : C6H6
  Name      : benzene
  Molwt     :  78.114    g/mol
  Tfp       :  278.7     K
  Tb        :  353.2     K
  Tc        :  562.2     K
  Pc        :  48.90     bar
  Vc        :  259.000   m3/mol
  Zc        :  0.271
  Omega     :  0.212
  Dipm      : 0
  CpA       : -33.92     J/mol-K
  CpB       :  0.4739    J/mol-K2
  CpC       : -3.0170e-04 J/mol-K3
  CpD       :  7.1300e-08 J/mol-K4
  dHf       :  82980.0   J/mol
  dGf       :  129700.0  J/mol
  Eq        : 1
  VpA       : -6.98273
  VpB       :  1.33213
  VpC       : -2.62863
  VpD       : -3.33399
  Tmin      :  288.0     K
  Tmax      :  562.2     K
  Lden      :  0.885
  Tden      :  289.0
$ sandlertools props find nitrosamine
nitrosamine not found.  Here are similars:
nitromethane
bromine
difluoroamine
nitrous oxide
n-eicosane
dipropylamine
n-propyl amine
nitrogen
isopropyl amine
nitric oxide
```

#### `sandlertools cubic`

Below are examples of using `sandlertools cubic` to perform volumetric calculations
for benzene using the Peng-Robinson, Van der Waals, and Ideal Gas equations of state.

```sh
$ sandlertools cubic state -T 800 -P 1.5 -n benzene -eos pr   
EOS  = pr
T    = 800.00 K
P    = 1.50 MPa
Z    = 0.97
v    = 0.004282 m3/mol
Hdep = -916.34 J/mol
Sdep = -0.86 J/mol-K
Tc    = 562.20 K
Pc    = 4.89 MPa
omega = 0.212
$ sandlertools cubic state -T 800 -P 1.5 -n benzene -eos vdw  
EOS  = vdw
T    = 800.00 K
P    = 1.50 MPa
Z    = 0.96
v    = 0.004268 m3/mol
Hdep = -691.82 J/mol
Sdep = -0.24 J/mol-K
Tc = 562.20 K
Pc = 4.89 MPa
$ sandlertools cubic state -T 800 -P 1.5 -n benzene -eos ideal
EOS = ideal
T   = 800.00 K
P   = 1.50 MPa
v   = 0.004434 m3/mol
```

#### `sandlertools steam`

Below is an example of using `sandlertools steam` to look up/interpolate properties in the steam tables.

```sh
$ sandlertools steam state -TC 404 -P 1.5
THERMODYNAMIC STATE OF UNSATURATED STEAM/WATER:
TC =  404.0 C =  677.1 K
P  =  1.50 MPa =  15.00 bar
u  =  2958.06 kJ/kg =  53290.3 J/mol
v  =  0.205216 m3/kg =  0.00369702 m3/mol
s  =  7.28203 kJ/kg-K =  131.188 J/mol-K
h  =  3264.54 kJ/kg =  58811.6 J/mol
$ sandlertools steam state --T 213 --x 0.5
THERMODYNAMIC STATE OF SATURATED STEAM/WATER:
TC =  213.0 C =  486.1 K
P  =  2.02 MPa =  20.25 bar
u  =  1754.78 kJ/kg =  31612.8 J/mol
v  =  0.0499079 m3/kg =  0.000899105 m3/mol
s  =  4.39471 kJ/kg-K =  79.1719 J/mol-K
h  =  1855.59 kJ/kg =  33428.9 J/mol
x  =  0.50 kg vapor/kg
uL =  909.096 kJ/kg =  16377.6 J/mol
uV =  2600.46 kJ/kg =  46848 J/mol
vL =  0.0011778 m3/kg =  2.12184e-05 m3/mol
vV =  0.098638 m3/kg =  0.00177699 m3/mol
sL =  2.45276 kJ/kg-K =  44.1872 J/mol-K
sV =  6.33666 kJ/kg-K =  114.157 J/mol-K
hL =  911.476 kJ/kg =  16420.5 J/mol
hV =  2799.7 kJ/kg =  50437.4 J/mol
```

#### `sandlertools cs`

Below is an example of using `sandlertools cs` to perform a volumetric state calculation on methane using Corresponding States.

```sh
$ sandlertools cs state -T 500 -P 15.5 -n methane
T    =  500.00 K
P    =  15.50 mpa
Tr   =  2.63
Pr   =  3.37
v    =  0.000260 m3/mol
Z    =  0.97
Hdep = -645.27 J/mol = -0.81 cal/mol-K
Sdep = -1.30 J/mol-K = -0.31 cal/mol-K
```

`sandlertools cs` can also perform change-of-state calculations, as demonstrated below:

```sh
sandlertools cs delta -T1 350 -P1 7.5 -T2 400 -P2 15.5 -n methane --show-states        
State 1:
T    =  350.00 K
P    =  7.50 mpa
Tr   =  1.84
Pr   =  1.63
v    =  0.000369 m3/mol
Z    =  0.95
Hdep = -621.37 J/mol = -0.78 cal/mol-K
Sdep = -1.55 J/mol-K = -0.37 cal/mol-K

State 2:
T    =  400.00 K
P    =  15.50 mpa
Tr   =  2.10
Pr   =  3.37
v    =  0.000204 m3/mol
Z    =  0.95
Hdep = -1043.59 J/mol = -1.31 cal/mol-K
Sdep = -2.30 J/mol-K = -0.55 cal/mol-K

Property differences:
Delta H = 1572.03 J/mol
Delta S = -1.47 J/mol-K
Delta U = 1177.09 J/mol

Constants used for calculations:
Tc  = 190.40 K
Pc  = 4.60 MPa
CpA = 19.25 J/mol-K
CpB = 5.213e-02 J/mol-K^2
CpC = 1.197e-05 J/mol-K^3
CpD = -1.132e-08 J/mol-K^4
```

#### `sandlertools chemeq`

Below is an example of solving a chemical equilibrium problem using `sandlertools chemeq`:

```sh
$ sandlertools chemeq solve --components hydrogen nitrogen ammonia -T 600 -P 100 -n0 3. 1. 0.
N_{H2}=1.2110 y_{H2}=0.4314
N_{N2}=0.4037 y_{N2}=0.1438
N_{NH3}=1.1926 y_{NH3}=0.4248
```

### API

`sandlertools` exposes several classes, objects, and functions from its component packages:

#### `PropertiesDatabase`

`PropertiesDatabase` is the pure-component properties database class from the `sandlerprops.properties` module.  Instantiating `PropertiesDatabase` generates a database object within the local scope.

```python
>>> from sandlertools import PropertiesDatabase
>>> P = PropertiesDatabase()
>>> m = P.get_compound('methane')
>>> m.Molwt
16.043
>>> P.U.Molwt
'g/mol'
>>> m.Tc
190.4
>>> P.U.Tc
'K'
>>> e = P.get_compound('ethanz')
ethanz not found.  Here are similars:
ethane
methane
ethanol
methanol
ethyl amine
ethylene
methylal
methyl amine
ethylbenzene
nitromethane
```

`sandlertools` also exposes the convenience function `get_database` that provides
the lazy with quick access to a global, singleton properties database.

```python
>>> from sandlertools import get_database
>>> d = get_database() # access to a global database rather than a local instance like in the example above
>>> m = d.get_compound('methane')
>>> m.Molwt
16.043
>>> d.U.Molwt
'g/mol'
>>> m.Tc
190.4
>>> d.U.Tc
'K'
```

#### `SandlerSteamState`

`SandlerSteamState` is the `State` class from the `sandlersteam.state` module.

```python
>>> from sandlertools import SandlerSteamState as State # equivalent to from sandlersteam.state import State
>>> state1 = State(TC=100.0, P=0.1)
>>> state1.h.item()  # enthalpy in kJ/kg as a np.float64
2676.2
>>> state1.u.item()  # internal energy in kJ/kg
2506.7
>>> state1.v.item()  # volume in m3/kg
1.6958
>>> state1.s.item()  # entropy in kJ/kg-K
7.3614
```
#### `IdealGasEOS`, `GeneralizedVDWEOS`, and `PengRobinsonEOS` 

```python
>>> from sandlertools import PengRobsinsonEOS
>>> from sandlertools import PropertiesDatabase
>>> db = ProperitesDatabase()
>>> m = db.get_compound('methane')
>>> s1 = PengRobinsonEOS(Tc=m.Tc, Pc=m.Pc/10, omega=m.Omega)
>>> s1.T = 400
>>> s1.P = 0.5
>>> s1.v.item()  # it is a np float
0.0066279171348771915
```
#### `CorrespondingStatesChartReader`

`CorrespondingStatesChartReader` is the chart-reader class from the `sandlercorrespondingstates.charts` module.

```python
>>> from sandlertools import CorrespondingStatesChartReader, GasConstant, PropertiesDatabase
>>> db = PropertiesDatabase()
>>> component = db.get_compound('methane')
>>> cs = CorrespondingStatesChartReader()
>>> Rpv = GasConstant("bar", "m3")
>>> result = cs.dimensionalized_lookup(T=400, P=0.5, Tc=component.Tc, Pc=component.Pc/10, R_pv=Rpv)
>>> print(result.report())
T  =  400.00 K
P  =  7.50 mpa
Tc =  190.40 K
Pc =  4.60 mpa
Tr =  2.10
Pr =  1.63
v  =  0.000435 m3/mol
Z  =  0.98
Hdep = -438.15 J/mol = -0.55 cal/mol-K
Sdep = -1.13 J/mol-K = -0.27 cal/mol-K
```

#### `Component`, `Reaction`, and `ChemEqSystem`

`sandlertools` API exposes the `Component`, `Reaction`, and `ChemEqSystem` of the `sandlerchemeq` package.

```python
>>> from sandlertools import get_database, Component, Reaction, ChemEqSystem
>>> d = get_database()
>>> hydrogen = Component.from_compound(d.get_compound('hydrogen (equilib)'), T=298.15, P=1.0)               
>>> nitrogen = Component.from_compound(d.get_compound('nitrogen'), T=298.15, P=1.0)
>>> system = ChemEqSystem(Components=[ammonia, nitrogen, hydrogen], N0=np.array([0.0, 1.0, 3.0]),
                              T=500.0, P=100.0)
>>> system.solve_lagrange()
>>> print(system.report())
N_{NH3}=1.6828 y_{NH3}=0.7262
N_{N2}=0.1586 y_{N2}=0.0684
N_{H2}=0.4757 y_{H2}=0.2053
```

#### Miscellaneous

The `GasConstant` class is from the `sandlermisc.gas_constant` module. The `DeltaH_IG` and `DeltaS_IG` functions are from the `sandlermisc.thermals` module.


## Release History
* 0.5.1
    * changed default banner behavior
* 0.5.0
    * reports versions of all tools in banner message
* 0.4.0
    * `sandlerchemeq` integration
* 0.3.0
    * `SteamRequest` implemented
* 0.2.0
    * updated readme
* 0.1.0
    * Initial release

## Meta

Cameron F. Abrams – cfa22@drexel.edu

Distributed under the MIT license. See ``LICENSE`` for more information.

[https://github.com/cameronabrams](https://github.com/cameronabrams/)

## Contributing

1. Fork it (<https://github.com/cameronabrams/sandlertools/fork>)
2. Create your feature branch (`git checkout -b feature/fooBar`)
3. Commit your changes (`git commit -am 'Add some fooBar'`)
4. Push to the branch (`git push origin feature/fooBar`)
5. Create a new Pull Request
