import { Function, Runtime } from 'aws-cdk-lib/aws-lambda';
import { Cors, LambdaIntegration, RequestValidator, RestApi } from 'aws-cdk-lib/aws-apigateway';
import { PythonFunction, PythonLayerVersion } from '@aws-cdk/aws-lambda-python-alpha';
import { Construct } from 'constructs';
import * as path from 'path';

/**
 * The properties required for the Discord Bot construct.
 */
export interface DiscordBotProps {
  readonly lambdaName: string;
}

/**
 * A CDK Construct for setting up a serverless Discord bot.
 */
export class DiscordBot extends Construct {
  /**
   * The constructor for building the stack.
   * @param {Construct} scope The Construct scope to create the Construct in.
   * @param {string} id The ID of the Construct to use.
   * @param {DiscordBotProps} props The properties to configure the Construct.
   */
  constructor(scope: Construct, id: string, props: DiscordBotProps) {
    super(scope, id);
    // Create the Lambda for handling Interactions from our Discord bot.
    const discordBotLambda = this._createLambda(props.lambdaName);
    // Create our API Gateway
    const discordBotAPI = new RestApi(this, 'discord-bot-api', {
      defaultCorsPreflightOptions: {
        allowOrigins: Cors.ALL_ORIGINS,
      },
    });
    const discordBotAPIValidator = new RequestValidator(this, 'discord-bot-api-validator', {
      restApi: discordBotAPI,
      validateRequestBody: true,
      validateRequestParameters: true,
    });

    // User authentication endpoint configuration
    const discordBotEventItems = discordBotAPI.root.addResource('event', {
      defaultCorsPreflightOptions: {
        allowOrigins: ['*'],
      },
    });

    // Transform our requests and responses as appropriate.
    const discordBotIntegration: LambdaIntegration = new LambdaIntegration(discordBotLambda, {
      proxy: false,
      requestTemplates: {
        'application/json': '{\r\n\
              "timestamp": "$input.params(\'x-signature-timestamp\')",\r\n\
              "signature": "$input.params(\'x-signature-ed25519\')",\r\n\
              "jsonBody" : $input.json(\'$\')\r\n\
            }',
      },
      integrationResponses: [
        {
          statusCode: '200',
        },
        {
          statusCode: '401',
          selectionPattern: '.*[UNAUTHORIZED].*',
          responseTemplates: {
            'application/json': 'invalid request signature',
          },
        },
      ],
    });

    // Add a POST method for the Discord APIs.
    discordBotEventItems.addMethod('POST', discordBotIntegration, {
      apiKeyRequired: false,
      requestValidator: discordBotAPIValidator,
      methodResponses: [
        {
          statusCode: '200',
        },
        {
          statusCode: '401',
        },
      ],
    });
  }

  _createLambda(lambdaName: string) : PythonFunction {
    return new PythonFunction(this, lambdaName, {
      entry: path.join(__dirname, '../../app/src'),
      runtime: Runtime.PYTHON_3_9,
      layers: [
        new PythonLayerVersion(this, `${lambdaName}-dependencies-layer`, {
          entry: path.join(__dirname, '../../app/src'),
          compatibleRuntimes: [Runtime.PYTHON_3_9]
        }),
      ],
    });
  }
}