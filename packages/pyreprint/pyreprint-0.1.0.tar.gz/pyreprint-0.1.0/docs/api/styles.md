# Styles API

Style registry and loading system.

## Registry

### StyleRegistry

::: pyreprint.styles.registry.StyleRegistry

### register_style

::: pyreprint.styles.registry.register_style

### get_style

::: pyreprint.styles.registry.get_style

### list_styles

::: pyreprint.styles.registry.list_styles

### apply_style

::: pyreprint.styles.registry.apply_style

## Loading

### load_styles_from_file

::: pyreprint.styles.loader.load_styles_from_file

### load_styles_from_yaml

::: pyreprint.styles.loader.load_styles_from_yaml

### load_styles_from_dict

::: pyreprint.styles.loader.load_styles_from_dict

## Built-in Styles

The following styles are available by default:

| Style | Description |
|-------|-------------|
| `section` | Lines above and below text |
| `header` | Text with underline |
| `divider` | Softer divider with dashes |
| `box` | Text surrounded by border |
| `banner` | Full-width centered text |
| `title` | Prominent title format |
| `quote` | Blockquote style with prefix |
| `bullet` | Bullet point format |
| `numbered` | Numbered item format |
| `highlight` | Attention markers |
| `warning` | Warning message format |
| `error` | Error message format |
| `success` | Success message format |
| `info` | Info message format |

