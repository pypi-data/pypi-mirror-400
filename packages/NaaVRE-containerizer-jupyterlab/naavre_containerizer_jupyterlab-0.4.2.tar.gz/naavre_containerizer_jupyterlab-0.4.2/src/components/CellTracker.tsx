import * as React from 'react';
import { NaaVREExternalService } from '../naavre-common/handler';
import { CellPreview, cellsToChartNode } from '../naavre-common/CellPreview';
import { NaaVRECatalogue } from '../naavre-common/types';
import { INotebookModel, NotebookPanel } from '@jupyterlab/notebook';
import { theme } from '../Theme';
import TableContainer from '@material-ui/core/TableContainer';
import {
  Button,
  FormControlLabel,
  TextField,
  ThemeProvider,
  Tooltip
} from '@material-ui/core';
import {
  Alert,
  Autocomplete,
  Box,
  Checkbox,
  LinearProgress
} from '@mui/material';
import CircularProgress from '@material-ui/core/CircularProgress';
import { emptyChart } from '../naavre-common/emptyChart';
import { IVREPanelSettings } from '../VREPanel';
import { CellIOTable } from './CellIOTable';
import { CellDependenciesTable } from './CellDependenciesTable';
import { detectType } from '../services/rTypes';
import { createCell } from './CellCreation';

interface IProps {
  notebook: NotebookPanel | null;
  settings: IVREPanelSettings;
}

const DefaultCell: NaaVRECatalogue.WorkflowCells.ICell = {
  title: '',
  description: '',
  version: 1,
  next_version: null,
  container_image: '',
  inputs: [],
  outputs: [],
  params: [],
  secrets: [],
  confs: [],
  dependencies: []
};

interface IState {
  baseImageSelected: boolean;
  baseImages: any[];
  cellAnalyzed: boolean;
  currentCell: NaaVRECatalogue.WorkflowCells.ICell;
  extractorError: string;
  isDialogOpen: boolean;
  loading: boolean;
  typeSelections: { [type: string]: boolean };
  forceContainerize: boolean;
}

const DefaultState: IState = {
  baseImageSelected: false,
  baseImages: [],
  cellAnalyzed: false,
  currentCell: DefaultCell,
  extractorError: '',
  isDialogOpen: false,
  loading: false,
  typeSelections: {},
  forceContainerize: false
};

export class CellTracker extends React.Component<IProps, IState> {
  state = DefaultState;
  cellPreviewRef: React.RefObject<CellPreview>;

  constructor(props: IProps) {
    super(props);
    this.cellPreviewRef = React.createRef();
  }

  loadBaseImages = async () => {
    NaaVREExternalService(
      'GET',
      `${this.props.settings.containerizerServiceUrl}/base-image-tags?virtual_lab=${this.props.settings.virtualLab}`
    )
      .then(resp => {
        if (resp.status_code !== 200) {
          throw `${resp.status_code} ${resp.reason}`;
        }
        return JSON.parse(resp.content);
      })
      .then(data => {
        const updatedBaseImages = Object.entries(data).map(([name, image]) => ({
          name,
          image
        }));
        console.log('updatedBaseImages');
        console.log(updatedBaseImages);
        this.setState({ baseImages: updatedBaseImages });
      })
      .catch(reason => {
        console.log(`Could not retrieve base image tags: ${reason}`);
        console.log(reason);
      });
  };

  resetState = () => {
    const newState = DefaultState;
    newState.baseImages = this.state.baseImages;
    this.setState(newState);
    if (this.cellPreviewRef.current !== null) {
      this.cellPreviewRef.current.updateChart(emptyChart);
    }
  };

  connectAndInitWhenReady = (notebook: NotebookPanel) => {
    notebook.context.ready.then(() => {
      if (this.props.notebook !== null) {
        this.props.notebook.content.activeCellChanged.connect(this.resetState);
        this.props.notebook.content.modelContentChanged.connect(
          this.resetState
        );
      }
    });
  };

  componentDidMount = async () => {
    this.setState({
      currentCell: {
        ...this.state.currentCell,
        virtual_lab: this.props.settings.virtualLab || undefined
      }
    });
    await this.loadBaseImages();
    if (this.props.notebook) {
      this.connectAndInitWhenReady(this.props.notebook);
    }
  };

  componentDidUpdate = async (
    prevProps: Readonly<IProps>,
    _prevState: Readonly<IState>
  ) => {
    const preNotebookId = prevProps.notebook ? prevProps.notebook.id : '';
    const notebookId = this.props.notebook ? this.props.notebook.id : '';

    if (preNotebookId !== notebookId) {
      if (prevProps.notebook) {
        prevProps.notebook.content.activeCellChanged.disconnect(
          this.resetState
        );
        prevProps.notebook.content.modelContentChanged.disconnect(
          this.resetState
        );
      }
      if (this.props.notebook) {
        this.connectAndInitWhenReady(this.props.notebook);
      }
    }
  };

  getKernel = async () => {
    const sessionContext = this.props.notebook!.context.sessionContext;
    const kernelObject = sessionContext?.session?.kernel; // https://jupyterlab.readthedocs.io/en/stable/api/interfaces/services.kernel.ikernelconnection-1.html#serversettings
    return (await kernelObject!.info).implementation;
  };

  getTypeSelections = (
    cell: NaaVRECatalogue.WorkflowCells.ICell
  ): { [type: string]: boolean } => {
    const typeSelections: { [type: string]: boolean } = {};
    [cell.inputs, cell.outputs, cell.params, cell.secrets].forEach(varList => {
      varList.forEach(v => (typeSelections[v.name] = v.type !== null));
    });
    return typeSelections;
  };

  extractCell = async (
    notebookModel: INotebookModel | null,
    cellIndex: number,
    save = false
  ) => {
    if (notebookModel === null) {
      return null;
    }
    const kernel = await this.getKernel();
    this.setState({
      loading: true,
      extractorError: ''
    });

    NaaVREExternalService(
      'POST',
      `${this.props.settings.containerizerServiceUrl}/extract_cell`,
      {},
      {
        virtual_lab: this.props.settings.virtualLab || undefined,
        data: {
          save: save,
          kernel,
          cell_index: cellIndex,
          notebook: notebookModel.toJSON()
        }
      }
    )
      .then(resp => {
        if (resp.status_code !== 200) {
          throw `${resp.status_code} ${resp.reason}`;
        }
        return JSON.parse(resp.content);
      })
      .then(data => {
        const extractedCell = data as NaaVRECatalogue.WorkflowCells.ICell;

        // Sort variable lists alphabetically
        const compareFn = (
          a: NaaVRECatalogue.WorkflowCells.IBaseVariable,
          b: NaaVRECatalogue.WorkflowCells.IBaseVariable
        ) => {
          if (a.name > b.name) {
            return 1;
          }
          if (a.name < b.name) {
            return -1;
          }
          return 0;
        };
        extractedCell.inputs.sort(compareFn);
        extractedCell.outputs.sort(compareFn);
        extractedCell.params.sort(compareFn);
        extractedCell.secrets.sort(compareFn);

        const typeSelections = this.getTypeSelections(extractedCell);

        this.setState({
          loading: false,
          cellAnalyzed: true,
          extractorError: '',
          currentCell: extractedCell,
          typeSelections: typeSelections
        });

        if (this.cellPreviewRef.current !== null) {
          this.cellPreviewRef.current.updateChart(
            cellsToChartNode([extractedCell])
          );
        }
      })
      .catch(reason => {
        console.log(reason);
        this.setState({
          loading: false,
          extractorError: String(reason)
        });
      });
  };

  onAnalyzeCell = () => {
    this.extractCell(
      this.props.notebook!.model,
      this.props.notebook!.content.activeCellIndex
    )
      .then(() => {})
      .catch(reason => {
        console.log('Error extracting cell', reason);
      });
  };

  onDetectType = async () => {
    this.setState({ loading: true });
    detectType({
      notebook: this.props.notebook,
      currentCell: this.state.currentCell
    })
      .then(res => {
        this.setState({
          currentCell: res.updatedCell,
          typeSelections: res.updatedTypeSelections
        });
        console.log(this.state);
      })
      .catch(error => {
        console.log(error);
      })
      .finally(() => {
        this.setState({ loading: false });
      });
  };

  removeVariable = async (
    variable: NaaVRECatalogue.WorkflowCells.IBaseVariable,
    variableCategory: 'inputs' | 'outputs' | 'params' | 'secrets'
  ) => {
    const updatedCell = this.state.currentCell;
    updatedCell[variableCategory] = updatedCell[variableCategory].filter(
      (v: NaaVRECatalogue.WorkflowCells.IBaseVariable) =>
        v.name !== variable.name
    );
    const updatedTypeSelection = this.state.typeSelections;
    delete updatedTypeSelection[variable.name];
    this.setState({
      currentCell: updatedCell,
      typeSelections: updatedTypeSelection
    });
    if (this.cellPreviewRef.current !== null) {
      this.cellPreviewRef.current.updateChart(cellsToChartNode([updatedCell]));
    }
  };

  updateVariableType = async (
    event: React.ChangeEvent<{ name?: string; value: unknown }>,
    variable: NaaVRECatalogue.WorkflowCells.IBaseVariable,
    variableCategory: 'inputs' | 'outputs' | 'params' | 'secrets'
  ) => {
    const updatedCell = this.state.currentCell;
    updatedCell[variableCategory].forEach(v => {
      if (v.name === variable.name) {
        v.type = String(event.target.value) || null;
      }
    });
    const updatedTypeSelection = this.state.typeSelections;
    updatedTypeSelection[variable.name] = true;
    this.setState({
      currentCell: updatedCell,
      typeSelections: updatedTypeSelection
    });
  };

  updateBaseImage = async (value: any) => {
    const updatedCell = this.state.currentCell;
    console.log('updateBaseImage', value);
    updatedCell.base_container_image = value;
    this.setState({
      baseImageSelected: true,
      currentCell: updatedCell
    });
  };

  allTypesSelected = () => {
    if (Object.values(this.state.typeSelections).length > 0) {
      return Object.values(this.state.typeSelections).reduce((prev, curr) => {
        return prev && curr;
      });
    }
    return false;
  };

  onContainerize = async () => {
    await createCell(
      this.state.currentCell,
      this.props.settings,
      this.state.forceContainerize
    );
  };

  render() {
    return (
      <ThemeProvider theme={theme}>
        <div>
          <CellPreview ref={this.cellPreviewRef} />
          <Button
            variant="contained"
            className={'naavre-containerizer-button'}
            onClick={this.onAnalyzeCell}
            color="primary"
            disabled={!this.state.currentCell || this.state.loading}
          >
            {this.state.loading ? (
              <CircularProgress size={24} color="inherit" />
            ) : (
              'Analyze cell'
            )}
          </Button>
          {this.state.currentCell.kernel?.toLowerCase() === 'irkernel' && (
            <Button
              variant="contained"
              className={'naavre-containerizer-button'}
              onClick={this.onDetectType}
              color="primary"
              disabled={
                !this.state.currentCell ||
                this.state.loading ||
                this.allTypesSelected()
              }
            >
              Detect types
            </Button>
          )}
          {this.state.extractorError && (
            <div>
              <Alert severity="error">
                <p>Notebook cannot be analyzed: {this.state.extractorError}</p>
              </Alert>
            </div>
          )}
          {this.state.loading ? (
            <div>
              {this.state.loading ? (
                <div>
                  <p className={'naavre-containerizer-preview'}>
                    <span>Analyzing notebook</span>
                    <br />
                    <span style={{ color: '#aaaaaa' }}>
                      This can take up to a minute
                    </span>
                  </p>
                  <Box
                    className={'naavre-containerizer-table'}
                    sx={{ width: '100%' }}
                  >
                    <LinearProgress />
                  </Box>
                </div>
              ) : (
                <TableContainer></TableContainer>
              )}
            </div>
          ) : (
            <div>
              {this.state.currentCell.inputs.length > 0 && (
                <CellIOTable
                  title={'Inputs'}
                  ioItems={this.state.currentCell.inputs}
                  updateType={(v, e) => this.updateVariableType(v, e, 'inputs')}
                  removeEntry={v => this.removeVariable(v, 'inputs')}
                ></CellIOTable>
              )}
              {this.state.currentCell.outputs.length > 0 && (
                <CellIOTable
                  title={'Outputs'}
                  ioItems={this.state.currentCell.outputs}
                  updateType={(v, e) =>
                    this.updateVariableType(v, e, 'outputs')
                  }
                  removeEntry={v => this.removeVariable(v, 'outputs')}
                ></CellIOTable>
              )}
              {this.state.currentCell.params.length > 0 && (
                <CellIOTable
                  title={'Parameters'}
                  ioItems={this.state.currentCell.params}
                  updateType={(v, e) => this.updateVariableType(v, e, 'params')}
                  removeEntry={v => this.removeVariable(v, 'params')}
                ></CellIOTable>
              )}
              {this.state.currentCell.secrets.length > 0 && (
                <CellIOTable
                  title={'Secrets'}
                  ioItems={this.state.currentCell.secrets}
                  updateType={(v, e) =>
                    this.updateVariableType(v, e, 'secrets')
                  }
                  removeEntry={v => this.removeVariable(v, 'secrets')}
                ></CellIOTable>
              )}
              {this.state.currentCell.dependencies.length > 0 && (
                <CellDependenciesTable
                  items={this.state.currentCell.dependencies}
                ></CellDependenciesTable>
              )}
              {this.state.cellAnalyzed && (
                <div>
                  <p className={'naavre-containerizer-preview'}>Base Image</p>
                  <Autocomplete
                    getOptionLabel={option => option.name}
                    options={this.state.baseImages}
                    disablePortal
                    onChange={(_event: any, newValue: any | null) => {
                      this.updateBaseImage(newValue.image);
                    }}
                    id="combo-box-demo"
                    sx={{ width: 330, margin: '20px' }}
                    renderInput={params => <TextField {...params} />}
                  />
                  <Tooltip title="Build the container image, even if the cell hasn't changed and the image already exists">
                    <FormControlLabel
                      label="Force recontainerization"
                      control={
                        <Checkbox
                          checked={this.state.forceContainerize}
                          onChange={event => {
                            this.setState({
                              forceContainerize: event.target.checked
                            });
                          }}
                        />
                      }
                      style={{ margin: '0.5rem' }}
                    />
                  </Tooltip>
                  <Button
                    variant="contained"
                    className={'naavre-containerizer-button'}
                    onClick={this.onContainerize}
                    color="primary"
                    disabled={
                      !this.allTypesSelected() ||
                      !this.state.baseImageSelected ||
                      this.state.loading
                    }
                    style={{
                      float: 'right'
                    }}
                  >
                    Containerize
                  </Button>
                </div>
              )}
            </div>
          )}
        </div>
      </ThemeProvider>
    );
  }
}
