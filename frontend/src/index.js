import React, { useEffect } from 'react';
import { Router, Route, Switch } from 'react-router-dom';
import ReactDOM from 'react-dom';
import Login from './login/Login';
import Account from './account/Account';
import Replicas from './replicas/Replicas';
import Users from './users/Users';
import Logs from './logs/Logs';
import NotFound from './notfound/NotFound';
import Patient from './patient/Patient';
import Files from './files/Files';
import Detail from './detail/Detail';
import history from './history';
import { init } from './ws';
// import './index.css';
import 'antd/dist/antd.css';

function App() {
  const params = new URLSearchParams(window.location.search);
  const tempKey = params.get('key');

  if (!tempKey) {
    if (!localStorage.getItem('userId')) {
      history.push('/login');
    }
  } else {
    localStorage.setItem('tempKey', tempKey);
  }
  useEffect(() => {
    init();
  }, []);

  return (
    <Router history={history}>
      <Switch>
        <Route exact path="/login" component={Login} />
        <Route exact path="/" component={Files} />
        <Route exact path="/account" component={Account} />
        <Route exact path="/replicas" component={Replicas} />
        <Route exact path="/users" component={Users} />
        <Route exact path="/logs" component={Logs} />
        <Route exact path="/patients/:id" component={Patient} />
        <Route exact path="/files/:id" component={Detail} />
        <Route component={NotFound} />
      </Switch>
    </Router>
  );
}

ReactDOM.render(<App />, document.getElementById('root'));
