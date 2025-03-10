/* eslint-disable @typescript-eslint/no-explicit-any */
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

/**
 * Vertica Connection Config
 */
export interface VerticaConnection {
  connectionArguments?: { [key: string]: string };
  connectionOptions?: { [key: string]: string };
  /**
   * Database of the data source. This is optional parameter, if you would like to restrict
   * the metadata reading to a single database. When left blank , OpenMetadata Ingestion
   * attempts to scan all the databases in Vertica.
   */
  database?: string;
  /**
   * Host and port of the data source.
   */
  hostPort?: string;
  /**
   * password to connect  to the Vertica.
   */
  password?: string;
  /**
   * SQLAlchemy driver scheme options.
   */
  scheme?: VerticaScheme;
  supportsMetadataExtraction?: boolean;
  supportsUsageExtraction?: boolean;
  /**
   * Service Type
   */
  type?: VerticaType;
  /**
   * username to connect  to the Vertica. This user should have privileges to read all the
   * metadata in Vertica.
   */
  username?: string;
}

/**
 * SQLAlchemy driver scheme options.
 */
export enum VerticaScheme {
  VerticaVerticaPython = 'vertica+vertica_python',
}

/**
 * Service Type
 *
 * Service type.
 */
export enum VerticaType {
  Vertica = 'Vertica',
}
