@ECHO OFF

for %%f in (*.ui) do (
  pyuic5 %%f -o %%~nf.py
)

for %%f in (*.qrc) do (
  pyrcc5 %%f -o ../%%~nf_rc.py
)
