import React, { useState, useRef } from 'react';
import { Button, Modal, Form, Input, Checkbox, message } from 'antd';
import { request } from '../helpers';

export const EditUserModal = Form.create({ name: 'edit_user' })(
  class extends React.Component {
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
            <Form.Item label="Username">
              {getFieldDecorator('username', {
                rules: [{ required: true, message: 'Please enter username!' }],
              })(<Input />)}
            </Form.Item>

            <Form.Item>
              {getFieldDecorator('admin', {
                initialValue: false,
              })(
                <Checkbox>Admin</Checkbox>
              )}
            </Form.Item>
          </Form>
        </Modal>
      );
    }
  });

export function AddUserFinish(props) {
  return (
    <Modal
      visible={props.visible}
      title="New user"
      okText="Ok"
      onCancel={props.onClose}
      footer={null}
    >
      <p>Username: {props.username}</p>
      <p>Password: {props.password}</p>
    </Modal>
  );
}

export function AddUser(props) {
  let [visible, setVisible] = useState(false);
  let [result, setResult] = useState({});
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
      request('users', { data: values }).then(data => {
        form.resetFields();
        setVisible(false);
        setResult({password: data.password, username: data.username});
      }).catch(e => {
        message.error(e.message);
      });
    });
  };

  const closeResult = () => {
    setResult({});
    props.reload();
  };

  return (
    <div style={props.style}>
      <Button type="primary" onClick={showModal}>
        Add user
      </Button>
      <AddUserFinish
        visible={result.password}
        password={result.password}
        username={result.username}
        onClose={closeResult}
      ></AddUserFinish>
      <EditUserModal
        title="Add user"
        okText="Add"
        wrappedComponentRef={saveFormRef}
        visible={visible}
        onCancel={handleCancel}
        onCreate={handleCreate}
      />
    </div>
  );
}
