import React, { ChangeEvent, useContext, useEffect, useState } from 'react';
import AutoModeIcon from '@mui/icons-material/AutoMode';
import Button from '@mui/material/Button';
import CheckCircleOutlineIcon from '@mui/icons-material/CheckCircleOutline';
import Stack from '@mui/material/Stack';
import TextField from '@mui/material/TextField';
import { green } from '@mui/material/colors';
import { grey } from '@mui/material/colors';
import { ThemeProvider } from '@mui/material/styles';
import { IChart } from '@mrblenny/react-flow-chart';

import {
  IParam,
  ISecret
} from '../../naavre-common/types/NaaVRECatalogue/WorkflowCells';
import { NaaVREExternalService } from '../../naavre-common/handler';
import { theme } from '../../Theme';
import { SettingsContext } from '../../settings';
import WorkflowRepeatPicker from '../WorkflowRepeatPicker';
import { runWorkflowNotification } from './runWorkflowNotification';
import DialogTitle from '@mui/material/DialogTitle';
import Dialog from '@mui/material/Dialog';
import DialogContent from '@mui/material/DialogContent';

interface IParamValue {
  value: string | null;
  default_value?: string;
}

interface ISecretValue {
  value: string | null;
}

// Partial type for POST {workflowServiceUrl}/submit
declare type SubmitWorkflowResponse = {
  run_url: string;
};

export function RunWorkflowDialog({
  open,
  onClose,
  chart
}: {
  open: boolean;
  onClose: () => void;
  chart: IChart;
}) {
  return (
    <Dialog onClose={onClose} open={open}>
      <DialogTitle>Run Workflow</DialogTitle>
      <DialogContent>
        <RunWorkflowDialogContent onClose={onClose} chart={chart} />
      </DialogContent>
    </Dialog>
  );
}

function RunWorkflowDialogContent({
  onClose,
  chart
}: {
  onClose: () => void;
  chart: IChart;
}) {
  const settings = useContext(SettingsContext);
  const [params, setParams] = useState<{ [name: string]: IParamValue }>({});
  const [secrets, setSecrets] = useState<{ [name: string]: ISecretValue }>({});
  const [cron, setCron] = useState<string | null>(null);
  const [submittedWorkflow, setSubmittedWorkflow] =
    useState<SubmitWorkflowResponse | null>(null);

  const setParam = (name: string, value: IParamValue) => {
    setParams(prevState => ({ ...prevState, [name]: value }));
  };
  const setSecret = (name: string, value: ISecretValue) => {
    setSecrets(prevState => ({ ...prevState, [name]: value }));
  };
  const isCron = cron !== null;

  useEffect(() => {
    const params: { [name: string]: IParamValue } = {};
    const secrets: { [name: string]: ISecretValue } = {};
    Object.values(chart.nodes).forEach(node => {
      node.properties.cell.params.forEach((param: IParam) => {
        params[param.name] = {
          value: null,
          default_value: param.default_value
        };
      });
      node.properties.cell.secrets.forEach((secret: ISecret) => {
        secrets[secret.name] = { value: null };
      });
    });
    setParams(Object.fromEntries(Object.entries(params).sort()));
    setSecrets(Object.fromEntries(Object.entries(secrets).sort()));
  }, [chart.nodes]);

  const updateParamValue = async (
    event: ChangeEvent<{ value: string }>,
    key: string
  ) => {
    setParam(key, {
      value: event.target.value,
      default_value: params[key].default_value
    });
  };

  const updateSecretValue = async (
    event: ChangeEvent<{ value: string }>,
    key: string
  ) => {
    setSecret(key, { value: event.target.value });
  };

  const allValuesFilled = () => {
    let all_filled = true;
    Object.values(params).forEach(param => {
      all_filled = all_filled && param.value !== null;
    });
    Object.values(secrets).forEach(secret => {
      all_filled = all_filled && secret.value !== null;
    });
    return all_filled;
  };

  const getValuesFromCatalog = async () => {
    Object.entries(params).forEach(([k, v]) => {
      setParam(k, {
        value: v.default_value || null,
        default_value: v.default_value
      });
    });
  };

  const runWorkflow = async (
    params: { [name: string]: any },
    secrets: { [name: string]: any }
  ) => {
    NaaVREExternalService(
      'POST',
      `${settings.workflowServiceUrl}/submit`,
      {},
      {
        virtual_lab: settings.virtualLab,
        naavrewf2: chart,
        params: params,
        secrets: secrets,
        cron_schedule: cron
      }
    )
      .then(resp => {
        if (resp.status_code !== 200) {
          throw `${resp.status_code} ${resp.reason}`;
        }
        const data: SubmitWorkflowResponse = JSON.parse(resp.content);
        setSubmittedWorkflow(data);
        if (!isCron) {
          runWorkflowNotification(data.run_url, settings);
        }
      })
      .catch(error => {
        const msg = `Error running the workflow: ${error}`;
        console.log(msg);
        alert(msg);
      });
  };

  return (
    <ThemeProvider theme={theme}>
      <div
        style={{
          display: 'flex',
          overflow: 'scroll',
          flexDirection: 'column'
        }}
      >
        {submittedWorkflow ? (
          <div>
            <div
              style={{
                padding: '10px',
                alignItems: 'center',
                display: 'flex',
                flexDirection: 'column'
              }}
            >
              <CheckCircleOutlineIcon
                fontSize="large"
                sx={{ color: green[500] }}
              />
              {isCron ? (
                <>
                  <p style={{ fontSize: 'large' }}>
                    Recurring workflow scheduled!
                  </p>
                  <p style={{ fontSize: 'medium' }}>
                    <a
                      style={{
                        textDecoration: 'underline',
                        color: 'var(--jp-content-link-color)'
                      }}
                      href={submittedWorkflow.run_url}
                      target="_blank"
                    >
                      Show in workflow engine
                    </a>
                  </p>
                </>
              ) : (
                <p style={{ fontSize: 'large' }}>Workflow submitted!</p>
              )}
            </div>
            <Stack
              direction="row"
              spacing={2}
              style={{
                float: 'right',
                alignItems: 'center'
              }}
            >
              <Button
                variant="contained"
                className={'lw-panel-button'}
                onClick={onClose}
                color="primary"
                style={{
                  float: 'right'
                }}
              >
                Ok
              </Button>
            </Stack>
          </div>
        ) : (
          <div>
            {Object.keys(params).length !== 0 && (
              <div
                style={{
                  textAlign: 'right',
                  padding: '10px 15px 10px 15px'
                }}
              >
                <Button
                  disabled={false}
                  onClick={getValuesFromCatalog}
                  size="small"
                  variant="text"
                  endIcon={<AutoModeIcon fontSize="inherit" />}
                  style={{ color: grey[900], textTransform: 'none' }}
                >
                  Use default parameter values
                </Button>
              </div>
            )}
            <Stack
              direction="column"
              spacing={2}
              style={{ width: '80vw', maxWidth: '100%' }}
            >
              {Object.entries(params).map(([k, v]) => (
                <TextField
                  key={k}
                  label={k}
                  slotProps={{ inputLabel: { shrink: true } }}
                  value={params[k].value}
                  onChange={e => updateParamValue(e, k)}
                />
              ))}
              {Object.entries(secrets).map(([k, v]) => (
                <TextField
                  key={k}
                  label={k}
                  slotProps={{ inputLabel: { shrink: true } }}
                  type="password"
                  autoComplete="off"
                  value={secrets[k].value}
                  onChange={e => updateSecretValue(e, k)}
                />
              ))}
            </Stack>
            <Stack
              direction="row"
              spacing={2}
              style={{
                float: 'right',
                marginTop: '2rem',
                alignItems: 'center'
              }}
            >
              <WorkflowRepeatPicker setCron={setCron} />
              <Button
                variant="contained"
                className={'lw-panel-button'}
                onClick={() => runWorkflow(params, secrets)}
                color="primary"
                disabled={!allValuesFilled()}
                style={{
                  float: 'right'
                }}
              >
                Run
              </Button>
            </Stack>
          </div>
        )}
      </div>
    </ThemeProvider>
  );
}
