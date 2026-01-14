import React from 'react';

import { NaaVRECatalogue } from '../naavre-common/types';

import {
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableRow
} from '@material-ui/core';

interface ICellDependenciesTable {
  items: Array<NaaVRECatalogue.WorkflowCells.IDependency>;
}

export const CellDependenciesTable: React.FC<ICellDependenciesTable> = ({
  items
}) => {
  return (
    <div>
      <p className={'naavre-containerizer-preview'}>Dependencies</p>
      <TableContainer
        component={Paper}
        className={'naavre-containerizer-table'}
      >
        <Table aria-label="simple table">
          <TableBody>
            {items.map((dep: any) => (
              <TableRow key={`${dep.module}-${dep.name}`}>
                <TableCell component="th" scope="row">
                  {dep['module'] !== ''
                    ? dep['module'] + ' • ' + dep['name']
                    : dep['name']}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </div>
  );
};
