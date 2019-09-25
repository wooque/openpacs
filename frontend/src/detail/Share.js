import React, { useState } from 'react';
import { withRouter } from 'react-router-dom';
import {
  Form, Input, InputNumber, Button, message, Layout, Modal, Row, Col,
} from 'antd';
import { request } from '../helpers';
const { Content } = Layout;


function Share(props) {
  document.title = 'Share';
  let [loading, setLoading] = useState(false);
  let [key, setKey] = useState(null);

  const { getFieldDecorator } = props.form;

  const handleSubmit = (event) => {
    event.preventDefault();
    setLoading(true);
    props.form.validateFields((err, values) => {
      if (!err) {
        request(`files/${props.file.id}/share`, { data: values })
          .then((data) => {
            setLoading(false);
            setKey(data.key);
          }).catch(() => {
            setLoading(false);
            message.error('Share failed');
          });
      }
    });
  };

  function copy() {
    var copyText = document.getElementById('key');

    copyText.select();
    copyText.setSelectionRange(0, 99999);

    document.execCommand('copy');
  }

  return (
    <Content style={{ padding: 24, background: '#fff', minHeight: 360, maxWidth: 600 }}>
      <Form onSubmit={handleSubmit} className="share-form">
        <Form.Item label="Duration (in hours)">
          {getFieldDecorator('duration', {
            initialValue: 1,
            rules: [{
              required: true,
              message: 'Please duration!',
            }],
          })(<InputNumber />)}
        </Form.Item>
        <Form.Item>
          <Button type="primary" htmlType="submit" className="login-form-button"
            loading={loading}>
            Share
          </Button>
        </Form.Item>
      </Form>
      {
        key !== null &&
        <Modal
          visible={key !== null}
          title='Link'
          footer={[]}
          onCancel={() => setKey(null)}
          onOk={() => setKey(null)}
        >
          <Row>
            <Col span={20}>
              <Input id='key' defaultValue={`${window.location.href}?key=${key}`} ></Input>
            </Col>
            <Col span={2}>
              <Button type="dashed" onClick={copy}>Copy</Button>
            </Col>
          </Row>
        </Modal>
      }
    </Content>
  );
}

const Wrapped = Form.create({ name: 'share' })(Share);
export default withRouter(Wrapped);
