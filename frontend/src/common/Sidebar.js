import React, { useState, useEffect } from 'react';
import { Link, withRouter } from 'react-router-dom';
import { Layout, Menu, Icon } from 'antd';
import { useFetch } from '../hooks';
import { isAdmin } from '../helpers';
import { PAGINATION } from '../config';
import './Sidebar.css';

const { Sider } = Layout;

function getKey(loc) {
  return loc === '/' ? 'files' : loc.slice(1);
}

function getOpenKey(key) {
  if (['replicas', 'users', 'logs'].includes(key)) {
    return 'admin';
  }
  return key;
}

function Sidebar(props) {
  const loc = props.history.location.pathname;

  let [collapsed, setCollapsed] = useState(false);
  const key = getKey(loc);
  let [selectedKey, setSelectedKey] = useState(key);
  let [openKey, setOpenKey] = useState(getOpenKey(key));

  const onCollapse = (collapsed) => {
    setCollapsed(collapsed);
  };

  const { exec } = useFetch('logout', { method: 'POST' });

  const handleLogout = async (e) => {
    e.preventDefault();
    await exec();
    localStorage.removeItem('userId');
    localStorage.removeItem('admin');
    localStorage.removeItem('token');
    props.history.push('/login');
  };

  useEffect(() => {
    const key = getKey(loc);
    setSelectedKey(key);
    setOpenKey(getOpenKey(key));
  }, [loc]);

  return (
    <Sider collapsible collapsed={collapsed} onCollapse={onCollapse} theme="dark"
      breakpoint="lg"
      collapsedWidth="0"
      onBreakpoint={broke => {
        if (broke) {
          PAGINATION.limit = 5;
        }
      }}
    >
      <Menu mode="inline" theme="dark"
        defaultOpenKeys={[openKey]} defaultSelectedKeys={[selectedKey]} >

        <Menu.Item key="files">
          <Link to="/">
            <Icon type="file-search" />
            <span className="nav-text">Files</span>
          </Link>
        </Menu.Item>

        <Menu.Item key="account">
          <Link to="/account">
            <Icon type="user" />
            <span className="nav-text">Account</span>
          </Link>
        </Menu.Item>
        {
          isAdmin() &&
          <Menu.SubMenu key="admin"
            title={
              <span>
                <Icon type="lock" />
                <span>Admin</span>
              </span>
            }>
            <Menu.Item key="replicas">
              <Link to="/replicas">
                <Icon type="database" />
                <span className="nav-text">Replicas</span>
              </Link>
            </Menu.Item>
            <Menu.Item key="users">
              <Link to="/users">
                <Icon type="team" />
                <span className="nav-text">Users</span>
              </Link>
            </Menu.Item>
            <Menu.Item key="logs">
              <Link to="/logs">
                <Icon type="align-left" />
                <span className="nav-text">Logs</span>
              </Link>
            </Menu.Item>
          </Menu.SubMenu>
        }
        <Menu.Item key="logout">
          <Link to="/logout" onClick={handleLogout}>
            <Icon type="logout" />
            <span className="nav-text">Logout</span>
          </Link>
        </Menu.Item>
      </Menu>
    </Sider>
  );
}

export default withRouter(Sidebar);