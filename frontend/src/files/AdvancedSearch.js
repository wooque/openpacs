import React from 'react';
import { Button, Modal, Row, Col, Input } from 'antd';

export default function AdvancedSearch(props) {
  return (
    <Modal
      visible={props.visible}
      title="Search"
      okText="Search"
      onCancel={props.onClose}
      onOk={() => props.onSearch()}
    >
      {props.fields.map((f, i) => (
        <Row key={i} style={{ paddingBottom: '5px' }}>
          <Col span={12} style={{ paddingRight: '5px' }}>
            {
              i < props.fixed ?
                <span>{f[0]}</span> :
                <Input value={f[0]} onChange={e => props.onChangeLabel(i, e)}></Input>
            }
          </Col>
          <Col span={10} style={{ paddingRight: '5px' }} >
            <Input value={f[1]} onChange={e => props.onChange(i, e)}></Input>
          </Col>
          <Col span={2}>
            {
              i >= props.fixed &&
              <Button icon="close" onClick={() => props.onRemove(i)}></Button>
            }
          </Col>
        </Row>
      ))}
      <Button type='primary' onClick={() => props.onAdd()}>Add</Button>
    </Modal>
  );
}