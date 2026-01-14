# lemniscat.plugin.filetransform
A plugin to transform one or more files into a lemniscat workflow

## Description
This plugin allows you to transform one or more files into a lemniscat workflow. This plugin replace all attributes in the file by the value of the variables in the lemniscat runtime.

**Supported formats:** JSON, YAML, HCL (Terraform)

For example, if you have a file `config.json` with the following content:
```json
{
  "url": "",
  "port": ""
}
```
and you have the following variables in your lemniscat workflow:
- url: "http://localhost"
- port: "8080"

the plugin will transform the file into:
```json
{
  "url": "http://localhost",
  "port": "8080"
}
```


## Usage
### Pre-requisites
In order to use this plugin, you need to add plugin into the required section of your manifest file.

```yaml
requirements:
  - name: lemniscat.plugin.filetransform
    version: 0.2.0
```

### Transform json file with variables
```yaml
- task: filetransform
  displayName: 'set json file'
  steps:
    - run
  parameters:
    folderPath: ${{ filepath }}
    fileType: json
    targetFiles: "*.json"
```

### Transform yaml file with variables
```yaml
- task: filetransform
  displayName: 'set yaml file'
  steps:
    - run
  parameters:
    folderPath: ${{ filepath }}
    fileType: yaml
    targetFiles: "*.yml"
```

### Transform HCL file with variables (Terraform)
```yaml
- task: filetransform
  displayName: 'set terraform configuration'
  steps:
    - run
  parameters:
    folderPath: ${{ filepath }}
    fileType: hcl
    targetFiles: "*.tf"
```

### Transform Terraform variables file (.tfvars)
```yaml
- task: filetransform
  displayName: 'set terraform variables'
  steps:
    - run
  parameters:
    folderPath: ${{ filepath }}
    fileType: hcl
    targetFiles: "*.tfvars"
```

## Inputs

### Parameters
- `folderPath`: The path of the folder where the files to transform are located
- `fileType`: The type of the file to transform. It can be `json`, `yaml`, or `hcl`
- `targetFiles`: The pattern of the files to transform. It can be a single file or a pattern like `*.json`, `*.yml`, `*.tf`, or `*.tfvars`

## Outputs

No outputs