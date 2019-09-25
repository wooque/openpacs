import React, { useEffect } from 'react';
import { withRouter } from 'react-router-dom';
import { useFetch } from '../hooks';
import { Form, Input, Button, Icon, message, Layout } from 'antd';
import './Login.css';
const { Content } = Layout;


function LoginForm(props) {
  document.title = 'Login';

  const { getFieldDecorator } = props.form;
  const { exec, showLoading, loading, data, error } = useFetch('login');

  useEffect(() => {
    if (!data) return;
    localStorage.setItem('userId', data.id);
    localStorage.setItem('admin', data.admin);
    localStorage.setItem('token', data.token);
    props.history.push('/');
  });

  useEffect(() => {
    if (!loading && error) {
      message.error(error.error || error);
    }
  }, [loading, error]);

  const handleSubmit = (event) => {
    event.preventDefault();
    props.form.validateFields((err, values) => {
      if (!err) {
        exec(
          true,
          {
            method: 'POST',
            body: JSON.stringify({ username: values.username, password: values.password }),
          }
        );
      }
    });
  };
  return (
    <Layout style={{
      'alignItems': 'center',
      'justifyContent': 'center',
      'height': '100%'
    }}
    >
      <Content style={{ 'marginTop': '200px' }}>
        <Form onSubmit={handleSubmit} className="login-form">
          <h1 style={{ 'fontSize': '32px', 'textAlign': 'center' }}>OpenPACS</h1>
          <Form.Item>
            {getFieldDecorator('username', {
              rules: [{ required: true, message: 'Please input your username!' }],
            })(
              <Input
                prefix={<Icon type="user" style={{ color: 'rgba(0,0,0,.25)' }} />}
                placeholder="Username"
              />,
            )}
          </Form.Item>
          <Form.Item>
            {getFieldDecorator('password', {
              rules: [{ required: true, message: 'Please input your password!' }],
            })(
              <Input
                prefix={<Icon type="lock" style={{ color: 'rgba(0,0,0,.25)' }} />}
                type="password"
                placeholder="Password"
              />,
            )}
          </Form.Item>
          <Form.Item>
            <Button type="primary" htmlType="submit" className="login-form-button"
              loading={showLoading}>
                Login
            </Button>
          </Form.Item>
        </Form>
      </Content>
    </ Layout>
  );
}

const WrappedLoginForm = Form.create({ name: 'login' })(LoginForm);

export default withRouter(WrappedLoginForm);
