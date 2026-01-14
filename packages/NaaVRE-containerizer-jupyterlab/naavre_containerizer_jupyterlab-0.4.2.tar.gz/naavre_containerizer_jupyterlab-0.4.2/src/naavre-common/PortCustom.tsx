import styled from 'styled-components';
import { IPortDefaultProps } from '@mrblenny/react-flow-chart';
import { Tooltip } from '@material-ui/core';
import * as React from 'react';

const PortContainerLeft = styled.div`
  display: flex;
  justify-content: flex-start;
`;

const PortContainerRight = styled.div`
  display: flex;
  justify-content: flex-end;
`;

const PortDot = styled.div`
  width: 20px;
  height: 20px;
  background: ${props => props.color};
  border-radius: 50%;
  cursor: pointer;
`;

const PortDotSpecial = styled.div`
  margin-top: 20px;
  width: 25px;
  height: 25px;
  background: cadetblue;
  border-radius: 5px;
  cursor: pointer;
`;

const PortLabelContainerLeft = styled.div`
  margin-left: 5px;
`;

const PortLabelContainerRight = styled.div`
  margin-right: 5px;
`;

const PortLabel = styled.span`
  display: inline-block;
  max-width: 100px;
  white-space: nowrap;
  overflow: hidden !important;
  text-overflow: ellipsis;
`;

export const PortCustom = (props: IPortDefaultProps) => {
  if (props.port.properties['special_node']) {
    return <PortDotSpecial />;
  }

  if (props.port.type === 'left') {
    return (
      <Tooltip title={props.port.id} placement="right">
        <PortContainerLeft>
          <PortDot color={props.port.properties.color} />
          <PortLabelContainerLeft>
            <PortLabel>{props.port.id}</PortLabel>
          </PortLabelContainerLeft>
        </PortContainerLeft>
      </Tooltip>
    );
  }

  if (props.port.type === 'right') {
    return (
      <Tooltip title={props.port.id} placement="left">
        <PortContainerRight>
          <PortLabelContainerRight>
            <PortLabel>{props.port.id}</PortLabel>
          </PortLabelContainerRight>
          <PortDot color={props.port.properties.color} />
        </PortContainerRight>
      </Tooltip>
    );
  }

  return <></>;
};
