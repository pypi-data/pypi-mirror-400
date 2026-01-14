import React from 'react';

import { NaaVRECatalogue } from '../naavre-common/types';

import {
  FormControl,
  IconButton,
  MenuItem,
  Paper,
  Select,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableRow
} from '@material-ui/core';
import CloseIcon from '@material-ui/icons/Close';

interface ICellIOTable {
  title: string;
  ioItems: Array<NaaVRECatalogue.WorkflowCells.IBaseVariable>;
  updateType: (
    event: React.ChangeEvent<{ name?: string; value: unknown }>,
    port: NaaVRECatalogue.WorkflowCells.IBaseVariable
  ) => Promise<void>;
  removeEntry: (
    v: NaaVRECatalogue.WorkflowCells.IBaseVariable
  ) => Promise<void>;
}

export const CellIOTable: React.FC<ICellIOTable> = ({
  title,
  ioItems,
  updateType,
  removeEntry
}) => {
  return (
    <div>
      <p className={'naavre-containerizer-preview'}>{title}</p>
      <TableContainer
        component={Paper}
        className={'naavre-containerizer-table'}
      >
        <Table aria-label="simple table">
          <TableBody>
            {ioItems.map(
              (ioItem: NaaVRECatalogue.WorkflowCells.IBaseVariable) => (
                <TableRow key={ioItem.name}>
                  <TableCell
                    component="th"
                    scope="row"
                    style={{
                      width: '70%',
                      maxWidth: '150px',
                      overflow: 'hidden'
                    }}
                  >
                    <p style={{ fontSize: '1em' }}>{ioItem.name}</p>
                  </TableCell>
                  <TableCell
                    component="th"
                    scope="row"
                    style={{
                      width: '15%'
                    }}
                  >
                    <FormControl fullWidth>
                      <Select
                        labelId="io-types-select-label"
                        id={ioItem.name + '-select'}
                        label="Type"
                        value={ioItem.type || ''}
                        error={ioItem.type === null}
                        onChange={event => {
                          updateType(event, ioItem);
                        }}
                      >
                        <MenuItem value={'int'}>Integer</MenuItem>
                        <MenuItem value={'float'}>Float</MenuItem>
                        <MenuItem value={'str'}>String</MenuItem>
                        <MenuItem value={'list'}>List</MenuItem>
                      </Select>
                    </FormControl>
                  </TableCell>
                  <TableCell
                    component="th"
                    scope="row"
                    style={{
                      width: '15%',
                      paddingLeft: '0',
                      paddingRight: '0'
                    }}
                  >
                    <IconButton
                      aria-label="delete"
                      onClick={() => removeEntry(ioItem)}
                    >
                      <CloseIcon />
                    </IconButton>
                  </TableCell>
                </TableRow>
              )
            )}
          </TableBody>
        </Table>
      </TableContainer>
    </div>
  );
};
