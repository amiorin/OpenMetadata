/*
 *  Copyright 2021 Collate
 *  Licensed under the Apache License, Version 2.0 (the "License");
 *  you may not use this file except in compliance with the License.
 *  You may obtain a copy of the License at
 *  http://www.apache.org/licenses/LICENSE-2.0
 *  Unless required by applicable law or agreed to in writing, software
 *  distributed under the License is distributed on an "AS IS" BASIS,
 *  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 *  See the License for the specific language governing permissions and
 *  limitations under the License.
 */

import { AxiosError } from 'axios';
import { observer } from 'mobx-react';
import { LoadingState } from 'Models';
import React, { useEffect, useState } from 'react';
import { useHistory } from 'react-router-dom';
import AppState from '../../AppState';
import { useAuthContext } from '../../authentication/auth-provider/AuthProvider';
import { createUser } from '../../axiosAPIs/userAPI';
import PageContainerV1 from '../../components/containers/PageContainerV1';
import CreateUserComponent from '../../components/CreateUser/CreateUser.component';
import { ROUTES } from '../../constants/constants';
import { CreateUser } from '../../generated/api/teams/createUser';
import { Role } from '../../generated/entity/teams/role';
import { EntityReference as UserTeams } from '../../generated/entity/teams/user';
import { useAuth } from '../../hooks/authHooks';
import jsonData from '../../jsons/en';
import { showErrorToast } from '../../utils/ToastUtils';

const CreateUserPage = () => {
  const { isAdminUser } = useAuth();
  const { isAuthDisabled } = useAuthContext();
  const history = useHistory();

  const [roles, setRoles] = useState<Array<Role>>([]);
  const [teams, setTeams] = useState<Array<UserTeams>>([]);
  const [status, setStatus] = useState<LoadingState>('initial');

  const goToUserListPage = () => {
    history.push(ROUTES.USER_LIST);
  };

  const handleCancel = () => {
    goToUserListPage();
  };

  /**
   * Handles error if any, while creating new user.
   * @param error AxiosError or error message
   * @param fallbackText fallback error message
   */
  const handleSaveFailure = (
    error: AxiosError | string,
    fallbackText?: string
  ) => {
    showErrorToast(error, fallbackText);
    setStatus('initial');
  };

  /**
   * Submit handler for new user form.
   * @param userData Data for creating new user
   */
  const handleAddUserSave = (userData: CreateUser) => {
    setStatus('waiting');
    createUser(userData)
      .then((res) => {
        if (res.data) {
          AppState.addUser(res.data);
          setStatus('success');
          setTimeout(() => {
            setStatus('initial');
            goToUserListPage();
          }, 500);
        } else {
          handleSaveFailure(
            jsonData['api-error-messages']['create-user-error']
          );
        }
      })
      .catch((err: AxiosError) => {
        handleSaveFailure(
          err,
          jsonData['api-error-messages']['create-user-error']
        );
      });
  };

  useEffect(() => {
    setRoles(AppState.userRoles);
  }, [AppState.userRoles]);
  useEffect(() => {
    setTeams(AppState.userTeams);
  }, [AppState.userTeams]);

  return (
    <PageContainerV1>
      <CreateUserComponent
        allowAccess={isAdminUser || isAuthDisabled}
        roles={roles}
        saveState={status}
        teams={teams}
        onCancel={handleCancel}
        onSave={handleAddUserSave}
      />
    </PageContainerV1>
  );
};

export default observer(CreateUserPage);
