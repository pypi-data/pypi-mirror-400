# petal-user-journey-coordinator

A petal for the DroneLeaf ecosystem.

## Description

This petal provides [describe your petal's functionality here].

## Installation

```bash
# For development
pdm install -G dev

# For production
pdm install
```

## Usage

This petal provides the following endpoints:

- `GET /health` - Health check endpoint that reports proxy requirements and status
- `GET /hello` - Simple hello world endpoint for testing

## Development

### Running Tests

```bash
pdm run pytest
```

### Debugging

Use the provided VS Code launch configuration to debug the petal:

1. Open VS Code in this directory
2. Set breakpoints in your plugin.py file
3. Press F5 to start debugging

### Required Proxies

This petal requires the following proxies (modify in `get_required_proxies()`):
- `redis` - For caching and communication
- `db` - For database operations

### Optional Proxies

This petal can optionally use (modify in `get_optional_proxies()`):
- `ext_mavlink` - For MAVLink communication

## API Documentation

### Health Check

```
GET /health
```

Returns health information including:
- Petal name and version
- Required and optional proxy lists
- Custom petal status information

### Hello World

```
GET /hello
```

Simple endpoint for testing connectivity.

## License

MIT License
