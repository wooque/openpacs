import React, { useState, useRef } from 'react';
import { Button, Modal, Form, Input, Select, message, InputNumber } from 'antd';
import { request } from '../helpers';

const Option = Select.Option;

const s3regions = [
  'eu-central-1', 'eu-west-1', 'eu-west-2', 'eu-west-3', 'eu-north-1',
  'us-east-2', 'us-east-1', 'us-west-2',
];

export const EditReplicaModal = Form.create({ name: 'edit_replica' })(
  class extends React.Component {
    constructor() {
      super();
      this.state = {
        type: 'local',
      };
      this.onTypeChanged = this.onTypeChanged.bind(this);
    }

    onTypeChanged(t) {
      this.setState(
        { type: t },
        () => {
          // this.props.form.validateFields(['location'], { force: true });
        },
      );
    }

    componentWillReceiveProps(props) {
      if (props.visible === true && this.props.visible === false) {
        this.setState({type: 'local'});
        this.props.form.resetFields();
      }
    }

    render() {
      const { visible, onCancel, onCreate, title, okText, form } = this.props;
      const { getFieldDecorator } = form;
      return (
        <Modal
          visible={visible}
          title={title}
          okText={okText}
          onCancel={onCancel}
          onOk={onCreate}
        >
          <Form layout="vertical">
            <Form.Item>
              {getFieldDecorator('type', {
                initialValue: 'local',
              })(
                <Select style={{ width: 150 }} onChange={this.onTypeChanged}>
                  <Option value="local">Local</Option>
                  <Option value="s3">Amazon S3</Option>
                  <Option value="b2">Backblaze B2</Option>
                </Select>
              )}
            </Form.Item>
            {
              <Form.Item label="Delay (in minutes)">
                {getFieldDecorator('delay', {
                  initialValue: 0,
                  rules: [{
                    required: true,
                    message: 'Please replica\'s delay!',
                  }],
                })(<InputNumber min={0} />)}
              </Form.Item>
            }
            {
              this.state.type === 'local'
              && <Form.Item label="Location">
                {getFieldDecorator('location', {})(<Input />)}
              </Form.Item>
            }
            {
              this.state.type === 'b2'
              && <Form.Item label="App key id">
                {getFieldDecorator('app_key_id', {
                  rules: [{
                    required: true,
                    message: 'Please enter app key id!',
                  }],
                })(<Input />)}
              </Form.Item>
            }
            {
              this.state.type === 'b2'
              && <Form.Item label="App key">
                {getFieldDecorator('app_key', {
                  rules: [{
                    required: true,
                    message: 'Please enter app key!',
                  }],
                })(<Input />)}
              </Form.Item>
            }
            {
              this.state.type === 's3'
              && <Form.Item label="Region">
                {getFieldDecorator('location', {
                  initialValue: s3regions[0],
                })(
                  <Select style={{ width: 120 }}
                    defaultActiveFirstOption={true}
                  >
                    {
                      s3regions.map(r => (
                        <Option key={r} value={r}>{r}</Option>
                      ))
                    }
                  </Select>
                )}
              </Form.Item>
            }
            {
              this.state.type === 's3'
              && <Form.Item label="Access key id">
                {getFieldDecorator('access_key_id', {
                  rules: [{
                    required: true,
                    message: 'Please enter access key id!',
                  }],
                })(<Input />)}
              </Form.Item>
            }
            {
              this.state.type === 's3'
              && <Form.Item label="Secret access key">
                {getFieldDecorator('secret_access_key', {
                  rules: [{
                    required: true,
                    message: 'Please enter secret access key!',
                  }],
                })(<Input />)}
              </Form.Item>
            }
          </Form>
        </Modal>
      );
    }
  });


export function AddReplica(props) {
  let [visible, setVisible] = useState(false);
  const saveFormRef = useRef(null);

  const showModal = () => {
    setVisible(true);
  };

  const handleCancel = () => {
    setVisible(false);
  };

  const handleCreate = () => {
    const { form } = saveFormRef.current.props;
    form.validateFields((err, values) => {
      if (err) {
        return;
      }
      request('replicas', { data: values }).then(() => {
        form.resetFields();
        setVisible(false);
      }).then(() => {
        props.reload();
      }).catch(() => {
        message.error('Replica addition failed');
      });
    });
  };

  return (
    <div style={props.style}>
      <Button type="primary" onClick={showModal}>
        Add replica
      </Button>
      <EditReplicaModal
        title="Add replica"
        okText="Add"
        wrappedComponentRef={saveFormRef}
        visible={visible}
        onCancel={handleCancel}
        onCreate={handleCreate}
      />
    </div>
  );
}
