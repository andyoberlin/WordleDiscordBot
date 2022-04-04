import { Stack, StackProps } from 'aws-cdk-lib';
import { Construct } from 'constructs';

import { DiscordBot } from './discord-bot';

export class CdkStack extends Stack {

  constructor(scope: Construct, id: string, props?: StackProps) {
    super(scope, id, props);

    // The code that defines your stack goes here
    const discordBot = new DiscordBot(this, 'wordle-discord-bot-construct', {
      lambdaName: 'wordle-discord-bot'
    });
  }
}
