import { NotebookPanel } from '@jupyterlab/notebook';
import { KernelMessage } from '@jupyterlab/services';
import { NaaVRECatalogue } from '../naavre-common/types';
import { Cell } from '@jupyterlab/cells';
import { IOutputAreaModel } from '@jupyterlab/outputarea';

export const detectType = async ({
  notebook,
  currentCell
}: {
  notebook: NotebookPanel | null;
  currentCell: NaaVRECatalogue.WorkflowCells.ICell;
}): Promise<{
  updatedCell: NaaVRECatalogue.WorkflowCells.ICell;
  updatedTypeSelections: { [key: string]: boolean };
}> => {
  const activeCell = notebook!.content.activeCell;
  if (!activeCell) {
    throw 'No cell selected';
  } else if (activeCell.model.type !== 'code') {
    throw 'Selected cell is not a code cell';
  }

  // Clear output of currently selected cell
  const cell = notebook!.content.activeCell;
  const codeCell = cell as Cell & { model: { outputs: IOutputAreaModel } };
  codeCell.model.outputs.clear();

  // Get kernel
  const kernel = notebook!.sessionContext.session?.kernel;
  if (!kernel) {
    throw 'No kernel found';
  }

  // Get original source code
  // const cellContent = currentCell.model.value.text;
  const cellContent = 'xyz';

  // Retrieve inputs, outputs, and params from extractedCell
  const extractedCell = currentCell;
  const inputs = extractedCell['inputs'];
  const outputs = extractedCell['outputs'];
  const params = extractedCell['params'];
  const types: { [key: string]: string | null } = {};
  inputs.forEach(v => (types[v.name] = v.type));
  outputs.forEach(v => (types[v.name] = v.type));
  params.forEach(v => (types[v.name] = v.type));

  // Function to send code to kernel and handle response
  const sendCodeToKernel = async (
    code: string,
    vars: string[]
  ): Promise<{ [key: string]: string }> => {
    const future = kernel.requestExecute({ code });
    const detectedTypes: { [key: string]: string } = {};

    return new Promise((resolve, reject) => {
      future.onIOPub = msg => {
        if (msg.header.msg_type === 'execute_result') {
          const m = msg as KernelMessage.IExecuteResultMsg;
          console.log('Execution Result:', m.content);
        } else if (msg.header.msg_type === 'display_data') {
          const m = msg as KernelMessage.IDisplayDataMsg;
          console.log('Display Data:', m.content);

          let typeString = m.content.data['text/html'] as string;
          typeString = typeString.replace(/['"]/g, '');
          const varName = vars[0];

          let detectedType: string | null;
          if (typeString === 'integer') {
            detectedType = 'int';
          } else if (typeString === 'character') {
            detectedType = 'str';
          } else if (typeString === 'double') {
            detectedType = 'float';
          } else if (typeString === 'list') {
            detectedType = 'list';
          } else {
            detectedType = types[varName];
          }

          if (detectedType !== null) {
            detectedTypes[varName] = detectedType;
          }

          const output = {
            output_type: 'display_data',
            data: {
              'text/plain': vars[0] + ': ' + m.content.data['text/html']
            },
            metadata: {}
          };

          codeCell.model.outputs.add(output);
          vars.shift();
        } else if (msg.header.msg_type === 'stream') {
          const m = msg as KernelMessage.IStreamMsg;
          console.log('Stream:', m);
        } else if (msg.header.msg_type === 'error') {
          const m = msg as KernelMessage.IErrorMsg;
          const output = {
            output_type: 'display_data',
            data: {
              'text/plain':
                'evalue' in m.content ? m.content.evalue : 'No data found'
            },
            metadata: {}
          };
          codeCell.model.outputs.add(output);
          console.error('Error:', m.content);
        }
      };

      future.onReply = msg => {
        if ((msg.content.status as string) === 'ok') {
          resolve(detectedTypes);
        } else if ((msg.content.status as string) === 'error') {
          reject(msg.content);
        }
      };
    });
  };

  // Create code with typeof() for inputs and params
  let inputParamSource = '';
  inputs.forEach(input => {
    inputParamSource += `\ntypeof(${input.name})`;
  });
  params.forEach(param => {
    inputParamSource += `\ntypeof(${param.name})`;
  });

  // Send code to check types of inputs and params
  const detectedInputParamTypes = await sendCodeToKernel(inputParamSource, [
    ...inputs.map(v => v.name),
    ...params.map(v => v.name)
  ]);
  console.log('Detected Input and Param Types:', detectedInputParamTypes);

  // Send original source code
  await kernel.requestExecute({ code: cellContent }).done;

  // Create code with typeof() for outputs
  let outputSource = '';
  outputs.forEach(output => {
    outputSource += `\ntypeof(${output.name})`;
  });

  // Send code to check types of outputs
  const detectedOutputTypes = await sendCodeToKernel(outputSource, [
    ...outputs.map(v => v.name)
  ]);
  console.log('Detected Output Types:', detectedOutputTypes);

  // Update the state with the detected types
  const newTypes = {
    ...types,
    ...detectedInputParamTypes,
    ...detectedOutputTypes
  };
  const updatedCell = { ...currentCell };
  const typeSelections: { [key: string]: boolean } = {};

  updatedCell.inputs.forEach(v => {
    if (v.name === v.name) {
      v.type = newTypes[v.name];
    }
    typeSelections[v.name] = newTypes[v.name] !== null;
  });
  updatedCell.outputs.forEach(v => {
    if (v.name === v.name) {
      v.type = newTypes[v.name];
    }
    typeSelections[v.name] = newTypes[v.name] !== null;
  });
  updatedCell.params.forEach(v => {
    if (v.name === v.name) {
      v.type = newTypes[v.name];
    }
    typeSelections[v.name] = newTypes[v.name] !== null;
  });

  return {
    updatedCell: updatedCell,
    updatedTypeSelections: typeSelections
  };
};
