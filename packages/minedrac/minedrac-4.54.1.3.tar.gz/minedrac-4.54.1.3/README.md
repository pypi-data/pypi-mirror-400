# MineDRAC

## Configuration

### Logging

You can manage the logging level with an env variable:

```
export LOG_LEVEL=DEBUG
```

### ICAT+

MineDRAC is configured to use the official ESRF icat+ server by default: https://icatplus.esrf.fr

It can be configured to use any other server via a configuration `.env` file or export the variable `icat_plus`
Example:

```
export icat_plus_server="http://localhost:8000"
```

You can find out which server is pointing to by using the command:

```
> minedrac config icat_plus
http://localhost:8083

```

### Commands

#### login

This command allows to get the token of a DB user (this will not work for user accounts). For getting your token you can access it via the data portal.

```
> minedrac login authentication --username reader --password ****
c99d6e5d-096b-45f1-bde3-c4322fe15251

```

#### Retrieve

This command family allows to retrieve data from ICAT via ICAT+.

##### Dataset

This method will return the json serialization of the datasets with the filters applied.

You can list the filters by typing:

```
minedrac retrieve dataset --help
```
