/**
 * Codes for errors generated within this library
 */
export declare const ZstdErrorCode: {
    readonly InvalidData: 0;
    readonly WindowSizeTooLarge: 1;
    readonly InvalidBlockType: 2;
    readonly FSEAccuracyTooHigh: 3;
    readonly DistanceTooFarBack: 4;
    readonly UnexpectedEOF: 5;
};
type ZEC = (typeof ZstdErrorCode)[keyof typeof ZstdErrorCode];
/**
 * An error generated within this library
 */
export interface ZstdError extends Error {
    /**
     * The code associated with this error
     */
    code: ZEC;
}
/**
 * Decompresses Zstandard data
 * @param dat The input data
 * @param buf The output buffer. If unspecified, the function will allocate
 *            exactly enough memory to fit the decompressed data. If your
 *            data has multiple frames and you know the output size, specifying
 *            it will yield better performance.
 * @returns The decompressed data
 */
export declare function decompress(dat: Uint8Array, buf?: Uint8Array): Uint8Array;
/**
 * Callback to handle data in Zstandard streams
 * @param data The data that was (de)compressed
 * @param final Whether this is the last chunk in the stream
 */
export type ZstdStreamHandler = (data: Uint8Array, final?: boolean) => unknown;
/**
 * Decompressor for Zstandard streamed data
 */
export declare class Decompress {
    private s;
    private c;
    private l;
    private z;
    /**
     * Creates a Zstandard decompressor
     * @param ondata The handler for stream data
     */
    constructor(ondata?: ZstdStreamHandler);
    /**
     * Pushes data to be decompressed
     * @param chunk The chunk of data to push
     * @param final Whether or not this is the last chunk in the stream
     */
    push(chunk: Uint8Array, final?: boolean): any;
    /**
     * Handler called whenever data is decompressed
     */
    ondata: ZstdStreamHandler;
}
export {};
