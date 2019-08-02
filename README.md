# shakemap-data-encoder
Prepare data for use with ShakeMap

### Installing the library
```
pip install git+https://github.com/mlmarius/shakemap-data-encoder.git#egg=shakemap_data_encoder
```

### Using the library:

```python
import shakemap_data_encoder as sde

# get content of the event.xml file
xmlstring = sde.get_event_xml(data)

# get content of the ci file
xmlstring = sde.get_ci_xml(data)
```