import React, { useEffect } from 'react';
import { withRouter } from 'react-router-dom';
import { useFetch } from '../hooks';
import withSidebar from '../common/base';
import { Form, Input, Button, Icon, message, Layout } from 'antd';
const { Content } = Layout;


function Account(props) {
  document.title = 'Account';

  const { getFieldDecorator } = props.form;
  const { exec, loading, data, error } = useFetch('change_password');

  useEffect(() => {
    if (!loading && error) {
      message.error(error.error || error);
    }
  }, [loading, error]);

  useEffect(() => {
    if (data && Object.keys(data).length === 0) {
      message.success('Password changed!');
    }
  }, [data]);

  const handleSubmit = (event) => {
    event.preventDefault();
    props.form.validateFields((err, values) => {
      if (!err) {
        exec(
          true,
          {
            method: 'POST',
            body: JSON.stringify({ password: values.password }),
          }
        );
      }
    });
  };

  const compareToFirstPassword = (rule, value, callback) => {
    if (value && value !== props.form.getFieldValue('password')) {
      callback('Password do not match!');
    } else {
      callback();
    }
  };

  return (
    <Content style={{ padding: 24, background: '#fff', minHeight: 360, maxWidth: 600 }}>
      <Form onSubmit={handleSubmit} className="change-password-form">
        <Form.Item>
          {getFieldDecorator('password', {
            rules: [
              { required: true, message: 'Please input your password!' },
            ],
          })(
            <Input
              prefix={<Icon type="lock" style={{ color: 'rgba(0,0,0,.25)' }} />}
              type="password"
              placeholder="Password"
            />,
          )}
        </Form.Item>
        <Form.Item>
          {getFieldDecorator('password2', {
            rules: [
              { required: true, message: 'Please repeat your new password!' },
              { validator: compareToFirstPassword },
            ],
          })(
            <Input
              prefix={<Icon type="lock" style={{ color: 'rgba(0,0,0,.25)' }} />}
              type="password"
              placeholder="Password repeated"
            />,
          )}
        </Form.Item>
        <Form.Item>
          <Button type="primary" htmlType="submit" className="login-form-button"
            loading={loading}>
                Change password
          </Button>
        </Form.Item>
      </Form>
    </Content>
  );
}

const WrappedAccountForm = Form.create({ name: 'account' })(Account);
export default withRouter(withSidebar(WrappedAccountForm));
